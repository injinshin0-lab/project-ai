import pandas as pd
import numpy as np
import os
from django.conf import settings
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from intelligence.models import (
    Bg_Product, 
    Bg_Order_Item, 
    Bg_Wishlist,
    Bg_Cart,
    Bg_Recent_product,
    Bg_Review,
    BgAiRecommendation
)
# 타 앱 모델 import (실제 앱 이름으로 변경 필수)
# from your_app_name.models import (
#   Bg_Order_item, Bg_Wishlist, Bg_Cart, Bg_Recent_product, Bg_Review
#)

class AiRecommender:
    def __init__(self):
        self.data_dir = os.path.join(settings.BASE_DIR, 'data')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.processed_csv = os.path.join(self.data_dir, 'processed_ratings.csv')
        self.result_csv = os.path.join(self.data_dir, 'final_recommendations.csv')
    
    def collect_data(self):
        """1단계: 모든 테이블 데이터를 수집하여 통합 CSV 생성"""
        # 가중치 설정 (비즈니스 로직에 맞게 조정 가능)
        w = {'order': 5.0, 'wish': 3.0, 'cart':2.0, 'recent': 1.0}

        # 데이터 수집 (Query -> DataFrame)
        # 1. 주문상품
        df_order = pd.DataFrame(list(Bg_Order_Item.objects.values('user_id', 'product_id'))).assign(rating=w['order'])
        # 2. 찜
        df_wish = pd.DataFrame(list(Bg_Wishlist.objects.values('user_id', 'product_id'))).assign(rating=w['wish'])
        # 3. 장바구니
        df_cart = pd.DataFrame(list(Bg_Cart.objects.values('user_id', 'product_id'))).assign(rating=w['cart'])
        # 4. 최근 본 상품
        df_recent = pd.DataFrame(list(Bg_Recent_product.objects.values('user_id', 'product_id'))).assign(rating=w['recent'])
        # 5. 리뷰 (평점 반영)
        df_review = pd.DataFrame(list(Bg_Review.objects.values('user_id', 'product_id', 'rating')))

        # user_id로 출력되지 않고 'user'로 출력되는 경우, 해결을 위한 아래 코드
        dfs = [df_order, df_wish, df_cart, df_recent, df_review]
        for df in dfs:
            if 'user' in df.columns:
                df.rename(columns={'user': 'user_id'}, inplace=True)
            if 'product' in df.columns:
                df.rename(columns={'product': 'prodcut_id'}, inplace=True)

        # 모든 데이터 병합
        combined = pd.concat(dfs, ignore_index=True)

        # 유저별, 상품별 합계 계산
        integrated = combined.groupby(['user_id', 'product_id'])['rating'].sum().reset_index()
        integrated.to_csv(self.processed_csv, index=False)
        print("Pre-processed data saved to CSV.")

    def run_analysis(self):
        # 2단계 협업 필터링 연산 수행
        df = pd.read_csv(self.processed_csv)
        pivot = df.pivot_table(index='user_id', columns='product_id', values='rating').fillna(0)

        # 정규화 (사용자 기준)
        pivot_scaled = pivot.apply(lambda x: (x - x.min()) / (x.max() - x.min()) if (x.max() - x.min()) != 0 else x, axis=1)        

        # 코사인 유사도 연산
        user_sim = cosine_similarity(csr_matrix(pivot_scaled.values))
        user_sim_df = pd.DataFrame(user_sim, index=pivot.index, columns=pivot.index)

        result = []
        for u_id in pivot.index:
            # 유사 유저 10명
            similar_users = user_sim_df[u_id].sort_values(ascending=False)[1:11].index
            # 내가 안 본 상품 중 유사 유저들이 높은 점수를 준 상위 10개 추출
            user_seen = pivot.loc[u_id]
            unseen_ids = user_seen[user_seen == 0].index
            recoms = pivot_scaled.loc[similar_users, unseen_ids].mean().sort_values(ascending=False).head(10)

            for p_id, score in recoms.items():
                if score > 0:
                    result.append({'userid': u_id, 'product_id': p_id, 'score': round(score, 4)})
        
        pd.DataFrame(result).to_csv(self.result_csv, index=False)

    def save_results_to_db(self):
        # 3단계: 결과 csv를 DB 테이블에 저장
        df = pd.read_csv(self.result_csv)
        BgAiRecommendation.objects.all().delete() # 기존 데이터 초기화

        new_records = [
            BgAiRecommendation(user_id=row['userid'], product_id=row['product_id'], score=row['score'])
            for _, row in df.iterrows()
        ]
        BgAiRecommendation.objects.bulk_create(new_records)
        print("DB Update Complete.")

