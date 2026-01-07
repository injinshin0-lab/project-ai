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
        # 1. 데이터 저장용 data 폴더 안 csv 파일 생성
        self.data_dir = os.path.join(settings.BASE_DIR, 'data')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.processed_csv = os.path.join(self.data_dir, 'processed_ratings.csv')
        self.result_csv = os.path.join(self.data_dir, 'final_recommendations.csv')
        
        print(f"--- AI 엔진 가동: Django ORM 직접 연결 모드 ---")
    
            
    def collect_data(self):
        # """2단계: 장고 DB의 행동 데이터를 수집하여 가중치 점수 합산"""
        w = {'order': 5.0, 'wish': 3.0, 'cart': 3.5, 'recent': 0.5}
        all_data = []

        # 주문(order) 데이터 수집 (Bg_Order_item -> Bg_Order 연결)
        order_qs = Bg_Order_item.objects.values('order__user_id', 'product_id')
        if order_qs.exists():
            df_order = pd.DataFrame(list(order_qs))
            df_order.columns = ['user_id', 'product_id']
            df_order['rating'] = w['order']
            all_data.append(df_order)

        # 기타 행동 데이터 (찜, 장바구니, 최근본)
        targets = [
            (Bg_Wishlist, w['wish']),
            (Bg_Cart, w['cart']),
            (Bg_Recent_product, w['recent']),
        ]

        for model, weight in targets:
            # list()로 감싸기 전에 QuerySet이 존재하는지 먼저 확인
            qs = model.objects.values('user_id', 'product_id')
            if qs.exists():
                df = pd.DataFrame(list(qs))
                df['rating'] = weight
                all_data.append(df)

        # 리뷰 데이터 별도 처리 (자체 rating이 있으므로)
        review_qs = Bg_Review.objects.values('user_id', 'product_id', 'rating')
        if review_qs.exists():
            all_data.append(pd.DataFrame(list(review_qs)))

        # 만약 모든 데이터가 하나도 없다면 종료
        if not all_data:
            print("!!! 경고: DB에 참조할 데이터(주문, 찜, 장바구니 등)가 하나도 없습니다.")
            return False

        # 데이터 합치기
        combined = pd.concat(all_data, ignore_index=True)

        # 최종 그룹화 및 저장
        integrated = combined.groupby(['user_id', 'product_id'])['rating'].sum().reset_index()
        integrated.to_csv(self.processed_csv, index=False)
        print(f"전처리된 데이터 저장 완료: {len(integrated)}개의 행을 찾았습니다.")
        return True

    def run_analysis(self):
        # 2단계 협업 필터링 연산 수행
        if not os.path.exists(self.processed_csv): return
        df = pd.read_csv(self.processed_csv)

        # 1. 피벗 테이블 생성 (사용자 x 아이템)
        # 결측치는 0으로 채우지 않고 NaN 상태로 (계산 시 제외하기 위함)
        pivot = df.pivot_table(index='user_id', columns='product_id', values='rating')

        # 2. 사용자별  평균 평점 계산
        user_means = pivot.mean(axis=1)

        # 3. 코사인 유사도 계산을 위해 결측치를 0으로 채운 데이터 준비
        pivot_filled = pivot.fillna(0)

        # 4. 코사인 유사도 계산
        user_sim = cosine_similarity(pivot_filled)
        user_sim_df = pd.DataFrame(user_sim, index=pivot.index, columns=pivot.index)

        # 유저별 관심 카테고리 목록 로드 (속도 최적화)
        user_interests_map = {}
        for mapping in Bg_User_category_mapping.objects.all():
            if mapping.user_id not in user_interests_map:
                user_interests_map[mapping.user_id] = set()
            user_interests_map[mapping.user_id].add(mapping.interest_category_id)

        # 상품-카테고리 매핑 로드 (가산점 부여용)
        product_cat_map = {
            m.product_id: m.interest_category_id 
            for m in Bg_Category_product_mapping.objects.all()
        }

        result = []
        # K-최근접 이웃 수 설정 (예: 나랑 가장 비슷한 10)
        K = 10

        for u_id in pivot.index:
            # user_interests_map에서 현재 유저의 관심 카테고리 세트를 가져옴
            user_interests = user_interests_map.get(u_id, set())

            # 나 자신을 제외하고 유사도가 높은 순으로 정렬된 이웃 추출
            sim_scores = user_sim_df[u_id].drop(index=u_id).sort_values(ascending=False)

            # 유사도가 0보다 큰 상위 K명의 이웃(Neighborhood) 선정
            nearest_neighbors = sim_scores[sim_scores > 0].head(K)
            if nearest_neighbors.empty: continue

            # 내가 아직 평가하지 않은 아이템(결측치) 찾기
            user_ratings = pivot.loc[u_id]
            unseen_items = user_ratings[user_ratings.isna()].index

            

            for p_id in unseen_items:
                # 이웃들 중 해당 아이템에 점수를 남긴 사람들만 추출
                neighbor_ratings = pivot.loc[nearest_neighbors.index, p_id].dropna()
                if not neighbor_ratings.empty:
                    # 해당 이웃들의 유사도 값 추출
                    relevant_sims = nearest_neighbors.loc[neighbor_ratings.index]
                    
                    # 예측 평점 = 나의 평균 + (이웃들의 (평점-평균) 가중합 / 유사도 합)
                    weighted_diff_sum = 0
                    for neighbor_id, rating in neighbor_ratings.items():
                        # 이웃의 평점에서 해당 이웃의 평균을 뺌 (평균 보정)
                        diff = rating - user_means[neighbor_id]
                        weighted_diff_sum += diff * relevant_sims[neighbor_id]
                    
                    sim_sum = relevant_sims.abs().sum()

                    if sim_sum > 0:
                        # 1. 사용자 기반 예측 점수 (CF Score)
                        cf_score = user_means[u_id] + (weighted_diff_sum / sim_sum)

                        # 2. 아이템 기반 가산점 (Category Bonus)
                        # 상품 카테고리가 유저의 관심사 리스트에 있으면 가산점 부여
                        category_bonus = 0
                        if product_cat_map.get(p_id) in user_interests:
                            # 카테고리 점수 + 1.5
                            category_bonus = 1.5
                        
                        # 3. 최종 하이브리드 점수
                        final_score = cf_score + category_bonus

                        # 나의 평균에 보정된 가중합을 더함
                        result.append({
                            'user_id': u_id, 
                            'product_id': p_id, 
                            'score': round(final_score, 4)
                        })

        if not result:
            print("!!! 알림: 추천 결과가 비어있습니다.")
            return

        # 최종 결과 저장
        res_df = pd.DataFrame(result).sort_values(by=['user_id', 'score'], ascending=[True, False])
        
        # 유저 상위 10개만
        res_df = res_df.groupby('user_id').head(10)

        res_df.to_csv(self.result_csv, index=False)
        print(f"--- 분석 완료: {len(res_df)}건 생성 ---")

    def save_results_to_db(self):
        # 3단계: 결과 csv를 DB 테이블에 저장
        if not os.path.exists(self.result_csv): return

        df = pd.read_csv(self.result_csv)

        # 기존 결과 삭제 후 새로운 결과 일괄 저장 
        Bg_AI_recommendation.objects.all().delete()

        new_records = [
            Bg_AI_recommendation(
                user_id=row['user_id'], 
                product_id=row['product_id'], 
                score=row['score']
            )
            for _, row in df.iterrows()
        ]
        
        Bg_AI_recommendation.objects.bulk_create(new_records)
        print("DB 업데이트 완료")
        


        # [필수] 외부 DB 적재 함수 호출 추가
        # self.export_to_external_db(df)
    # def export_to_external_db(self, df):
    #     #"""최종 결과를 메인 DB의 Bg_ai_recommendation 테이블로 적재"""
    #     try:
    #         conn = sqlite3.connect(self.external_db_path)
    #         cursor = conn.cursor()

    #         # 1. 테이블명과 컬럼명을 외부 DB 형식에 맞춤
    #         # df['userid'] 값을 외부 DB의 'user_id' 컬럼에 넣어야 함
    #         cursor.execute('''CREATE TABLE IF NOT EXISTS Bg_AI_recommendation 
    #                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                           user_id INTEGER NOT NULL, 
    #                           product_id INTEGER NOT NULL, 
    #                           score REAL NOT NULL,
    #                           created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    #                           expired_at DATETIME)''')
            
    #         # 2. 기존 데이터 삭제
    #         cursor.execute("DELETE FROM Bg_AI_recommendation")
    #         # ID 값도 초기화하고 싶다면 아래 주석 해제 (선택사항)
    #         cursor.execute("DELETE FROM sqlite_sequence WHERE name='Bg_AI_recommendation'")

    #         # 3. 데이터 삽입 (df의 컬럼명과 DB 컬럼명 매핑 주의)
    #         for _, row in df.iterrows():
    #             cursor.execute(
    #                 "INSERT INTO Bg_AI_recommendation (user_id, product_id, score) VALUES (?, ?, ?)",
    #                 (int(row['userid']), int(row['product_id']), float(row['score']))
    #             )
            
    #         conn.commit()
    #         conn.close()
    #         print(f"--- 외부 DB(Bg_AI_recommendation) 적재 완료 ---")
    #     except Exception as e:
    #         print(f"DB 적재 중 에러 발생: {e}")