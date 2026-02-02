import pandas as pd
import numpy as np
import os
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
from intelligence.models import (
    Bg_User, Bg_Product, Bg_Interest_category,
    Bg_Review, Bg_Wishlist, Bg_Cart, Bg_Recent_product,
    Bg_Order, Bg_Order_item, Bg_Category_product_mapping, 
    Bg_User_category_mapping, Bg_AI_recommendation
)

class AiRecommender:
    def __init__(self):
        self.data_dir = os.path.join(settings.BASE_DIR, 'data')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.processed_csv = os.path.join(self.data_dir, 'processed_ratings.csv')
        self.result_csv = os.path.join(self.data_dir, 'final_recommendations.csv')
        print(f"--- AI 엔진 가동: Django ORM 직접 연결 모드 ---")

    def collect_data(self):
        """1단계: DB 행동 데이터를 수집하여 가중치 점수 합산"""
        w = {'order': 5.0, 'wish': 3.0, 'cart': 4.0, 'recent': 1.0}
        all_data = []

        # 주문 데이터
        order_qs = Bg_Order_item.objects.values('order__user_id', 'product_id')
        if order_qs.exists():
            df_order = pd.DataFrame(list(order_qs))
            df_order.columns = ['user_id', 'product_id']
            df_order['rating'] = w['order']
            all_data.append(df_order)

        # 기타 행동 데이터
        targets = [(Bg_Wishlist, w['wish']), (Bg_Cart, w['cart']), (Bg_Recent_product, w['recent'])]
        for model, weight in targets:
            qs = model.objects.values('user_id', 'product_id')
            if qs.exists():
                df = pd.DataFrame(list(qs))
                df['rating'] = weight
                all_data.append(df)

        # 리뷰 데이터
        review_qs = Bg_Review.objects.values('user_id', 'product_id', 'rating')
        if review_qs.exists():
            all_data.append(pd.DataFrame(list(review_qs)))

        if not all_data:
            print("!!! 경고: 참조할 행동 데이터가 없습니다.")
            return False

        combined = pd.concat(all_data, ignore_index=True)
        integrated = combined.groupby(['user_id', 'product_id'])['rating'].max().reset_index()
        integrated.to_csv(self.processed_csv, index=False)
        print(f"전처리 완료: {len(integrated)}건 저장")
        return True

    def run_analysis(self):
        """2단계: 협업 필터링 + 카테고리 매칭 하이브리드 분석"""
        if not os.path.exists(self.processed_csv): return
        df = pd.read_csv(self.processed_csv)

        # 피벗 테이블 및 유사도 계산
        pivot = df.pivot_table(index='user_id', columns='product_id', values='rating')
        user_means = pivot.mean(axis=1)
        pivot_filled = pivot.fillna(0)
        user_sim = cosine_similarity(pivot_filled)
        user_sim_df = pd.DataFrame(user_sim, index=pivot.index, columns=pivot.index)

        # 매핑 데이터 로드 (속도 최적화)
        product_cat_map = {}
        for m in Bg_Category_product_mapping.objects.all():
            product_cat_map.setdefault(m.product_id, set()).add(m.interest_category_id)

        user_interests_map = {}
        for m in Bg_User_category_mapping.objects.all():
            user_interests_map.setdefault(m.user_id, set()).add(m.interest_category_id)

        all_user_ids = Bg_User.objects.values_list('id', flat=True)
        all_product_ids = set(Bg_Product.objects.values_list('id', flat=True))

        result = []
        K = 10

        for u_id in all_user_ids:
            user_interests = user_interests_map.get(u_id, set())
            
            # 이미 주문한 상품은 추천 제외
            ordered_ids = set(Bg_Order_item.objects.filter(order__user_id=u_id).values_list('product_id', flat=True))
            unseen_items = all_product_ids - ordered_ids

            # 이웃 찾기
            nearest_neighbors = pd.Series(dtype=float)
            if u_id in pivot.index:
                sim_scores = user_sim_df[u_id].drop(index=u_id).sort_values(ascending=False)
                nearest_neighbors = sim_scores[sim_scores > 0].head(K)

            user_temp_candidates = []
            
            for p_id in unseen_items:
                cf_score = 0
                # A. 협업 필터링 점수 계산
                if not nearest_neighbors.empty:
                    neighbor_ratings = pivot.loc[nearest_neighbors.index, p_id].dropna()
                    if not neighbor_ratings.empty:
                        relevant_sims = nearest_neighbors.loc[neighbor_ratings.index]
                        weighted_diff_sum = sum((rating - user_means[n_id]) * relevant_sims[n_id] 
                                                for n_id, rating in neighbor_ratings.items())
                        sim_sum = relevant_sims.abs().sum()
                        if sim_sum > 0:
                            cf_score = user_means[u_id] + (weighted_diff_sum / sim_sum)

                # B. 카테고리 매칭 점수 계산
                product_cats = product_cat_map.get(p_id, set())
                match_count = len(user_interests.intersection(product_cats)) if user_interests else 0

                user_temp_candidates.append({
                    'product_id': p_id,
                    'raw_cf': cf_score,
                    'match_count': match_count
                })

            # C. 점수 정규화 및 최종 합산
            if user_temp_candidates:
                raw_scores = [c['raw_cf'] for c in user_temp_candidates]
                max_s, min_s = max(raw_scores), min(raw_scores)

                for item in user_temp_candidates:
                    # CF 점수를 10점 만점으로 변환 (Min-Max Scaling)
                    if max_s > min_s:
                        norm_cf = ((item['raw_cf'] - min_s) / (max_s - min_s)) * 10
                    else:
                        norm_cf = 5.0 if max_s > 0 else 0.0
                    
                    # 최종 점수 = 정규화된 CF점수 + (매칭 카테고리 수 * 2점 보너스)
                    final_score = norm_cf + (item['match_count'] * 2.0)

                    if final_score > 0:
                        result.append({
                            'user_id': u_id, 
                            'product_id': item['product_id'], 
                            'score': round(final_score, 4)
                        })

        if not result:
            print("!!! 알림: 추천 결과가 비어있습니다.")
            return

        res_df = pd.DataFrame(result).sort_values(by=['user_id', 'score'], ascending=[True, False])
        res_df = res_df.groupby('user_id').head(10)
        res_df.to_csv(self.result_csv, index=False)
        print(f"--- 분석 완료: {len(res_df)}건 생성 ---")

    def save_results_to_db(self):
        """3단계: 분석 결과를 DB에 저장"""
        if not os.path.exists(self.result_csv): return
        df = pd.read_csv(self.result_csv)
        
        Bg_AI_recommendation.objects.all().delete()
        new_records = [
            Bg_AI_recommendation(user_id=row['user_id'], product_id=row['product_id'], score=row['score'])
            for _, row in df.iterrows()
        ]
        Bg_AI_recommendation.objects.bulk_create(new_records)
        print("DB 업데이트 완료")