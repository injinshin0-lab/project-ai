import pandas as pd
import numpy as np
import os
import sqlite3
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
    def __init__(self, external_db_path=None):
        self.data_dir = os.path.join(settings.BASE_DIR, 'data')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.processed_csv = os.path.join(self.data_dir, 'processed_ratings.csv')
        self.result_csv = os.path.join(self.data_dir, 'final_recommendations.csv')

        # [수정] 외부 DB 경로 설정 (나중에 담당자가 경로를 주면 이 부분만 바꾸면 됨)
        self.external_db_path = external_db_path or os.path.join(settings.BASE_DIR, 'aiprojectdb.db')

    def sync_from_external(self):
        """[추가] 외부 DB 담당자의 상품 목록을 내 임시 테이블(Bg_Product)로 복사"""
        if not os.path.exists(self.external_db_path):
            print(f"!!! 경고: 외부 DB 파일이 없습니다. 경로: {self.external_db_path}")
            return
        conn = sqlite3.connect(self.external_db_path)
        cursor = conn.cursor()

        # 1. 카테고리 정보 가져오기 (Bg_Category 모델이 있다고 가정)
        cursor.execute("SELECT id, name FROM category")
        for c_id, c_name in cursor.fetchall():
            # Bg_Category.objects.get_or_create(id=c_id, name=c_name)
            pass # 실제 모델명에 맞춰 저장

        # 2. 상품-카테고리 매핑 정보 가져오기
        cursor.execute("SELECT product_id, category_id FROM product_category_mapping")
        for p_id, c_id in cursor.fetchall():
            # Bg_Category.objects.get_or_create(id=c_id, name=C-name)
            pass

        # 3. 백엔드 담당자의 DB의 테이블명/칼럼명이 다르면 여기 쿼리만 수정
        cursor.execute("SELECT id, name FROM product")
        rows = cursor.fetchall()

        for row_id, row_name in rows:
            Bg_Product.objects.get_or_create(id=row_id, name=row_name)
        
        conn.close()
        print(f"--- 동기화 완료: 외부 DB 상품 정보를 로드했습니다. ---")

            
    def collect_data(self):
        """1단계: 모든 테이블 데이터를 수집하여 통합 CSV 생성"""
        w = {'order': 5.0, 'wish': 3.0, 'cart': 2.0, 'recent': 1.0}
        all_data = []

        # 수집할 타겟 모델과 가중치 매핑
        targets = [
            (Bg_Order_Item, w['order']),
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
            return

        # 데이터 합치기
        combined = pd.concat(all_data, ignore_index=True)

        # 컬럼명 정리 (장고 외래키 특성상 'user'나 'product'로 나올 수 있어 강제 지정)
        rename_dict = {
            'user': 'user_id', 
            'product': 'product_id', 
            'prodcut_id': 'product_id' # 혹시 모를 오타 방지
        }
        combined.rename(columns=rename_dict, inplace=True)

        # 최종 그룹화 및 저장
        integrated = combined.groupby(['user_id', 'product_id'])['rating'].sum().reset_index()
        integrated.to_csv(self.processed_csv, index=False)
        print(f"Pre-processed data saved: {len(integrated)} rows found.")

    def run_analysis(self):
        # 2단계 협업 필터링 연산 수행
        if not os.path.exists(self.processed_csv): return

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
        print("Analysis Complete.")

    def save_results_to_db(self):
        # 3단계: 결과 csv를 DB 테이블에 저장

        if not os.path.exists(self.result_csv): return

        df = pd.read_csv(self.result_csv)

        # 3-1 내 임시 DB 초기화 및 저장
        BgAiRecommendation.objects.all().delete() # 기존 데이터 초기화

        new_records = [
            BgAiRecommendation(user_id=row['userid'], product_id=row['product_id'], score=row['score'])
            for _, row in df.iterrows()
        ]
        BgAiRecommendation.objects.bulk_create(new_records)
        print("DB Update Complete.")

    def export_to_external_db(self, df):
        # 3-1 [추가] 계산된 추천 결과를 외부 DB의 테이블로 적재
        try:
            conn = sqlite3.connect(self.external_db_path)
            cursor = conn.cursor()

            # 외부 DB에 결과 테이블이 없으면 생성 (테이블명은 담당자와 협의)
            cursor.execute('''CREATE TABLE IF NOT EXISTS ai_recommendations 
                             (user_id INTEGER, product_id INTEGER, score REAL)''')
            
            # 기존 데이터 삭제 후 새로 적재 (Overwrite 방식)
            cursor.execute("DELETE FROM ai_recommendations")

            for _, row in df.iterrows() :
                cursor.execute(
                    "INSERT INTO ai_recommendations (user_id, product_id, score) VALUES (?, ?, ?)",
                    (int(row['userid']), int(row['product_id']), float(row['score']))
                )
            conn.commit()
            conn.close()
            print(f"--외부 DB 적재 완료: {self.external_db_path}---")
        except Exception as e:
            print(f"외부 DB 적재 중 에러 발생: {e}")

    