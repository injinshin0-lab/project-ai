# import sqlite3
# from django.core.management.base import BaseCommand

# class Command(BaseCommand):
#     help = '외부 SQLite DB에 테스트 데이터를 생성합니다.'

#     def handle(self, *args, **options):
#         # 1. 외부 DB 연결 (경로 확인 필수)
#         db_path = r"C:\AImy\Workspace\bogam\project.db"
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()

#         self.stdout.write("--- 기존 데이터 초기화 중 ---")
#         tables = ['bg_user', 'bg_product', 'bg_cart', 'bg_wishlist', 'bg_recent_product', 'bg_review', 'bg_order', 'bg_order_item']
#         for table in tables:
#             try:
#                 cursor.execute(f"DELETE FROM {table}")
#                 cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
#             except sqlite3.OperationalError as e:
#                 self.stdout.write(self.style.WARNING(f"테이블 {table} 삭제 중 건너뜀: {e}"))

#         # 2. 가짜 유저 데이터
#         users = [
#             (1, 'user1', '1234', '홍길동', '010-1111-1111', 'user1@test.com', '12345', '서울시', '강남구'),
#             (2, 'user2', '1234', '김철수', '010-2222-2222', 'user2@test.com', '23456', '부산시', '해운대구'),
#             (3, 'user3', '1234', '이영희', '010-3333-3333', 'user3@test.com', '34567', '대구시', '수성구'),
#         ]
#         cursor.executemany("""
#             INSERT INTO bg_user (id, login_id, password, name, phone, email, zipcode, address, address_detail) 
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#         """, users)

#         # 3. 가짜 상품 데이터
#         products = [
#             (101, '유기농 사과', 15000, 100, 'SALE', '국산'),
#             (102, '고당도 수박', 25000, 50, 'SALE', '국산'),
#             (103, '상주 샤인머스캣', 30000, 80, 'SALE', '국산'),
#             (104, '제주 한라봉', 18000, 120, 'SALE', '국산'),
#             (105, '꿀참외', 12000, 200, 'SALE', '국산'),
#         ]
#         cursor.executemany("""
#             INSERT INTO bg_product (id, product_name, price, stock, product_status, origin_name) 
#             VALUES (?, ?, ?, ?, ?, ?)
#         """, products)

#         # 4. 행동 데이터
#         wish_data = [
#             (1, 101), (1, 102), (2, 101), (2, 102), (2, 103), (3, 105)
#         ]
#         cursor.executemany("INSERT INTO bg_wishlist (user_id, product_id) VALUES (?, ?)", wish_data)

#         cart_data = [(1, 101, 2), (2, 103, 1)]
#         cursor.executemany("INSERT INTO bg_cart (user_id, product_id, quantity) VALUES (?, ?, ?)", cart_data)

#         recent_data = [(1, 104), (2, 104)]
#         cursor.executemany("INSERT INTO bg_recent_product (user_id, product_id) VALUES (?, ?)", recent_data)

#         review_data = [
#             (101, 1, '정말 맛있어요!', 5),
#             (102, 2, '달고 시원합니다.', 5)
#         ]
#         cursor.executemany("INSERT INTO bg_review (product_id, user_id, content, rating) VALUES (?, ?, ?, ?)", review_data)

#         # 5. 주문 데이터 추가 (AI에게 5.0점짜리 강력한 힌트 주기)
#         # 먼저 주문 마스터 기록 생성
#         # 필드: id, user_id, address_id, order_status, ordered_at, payment_method, payment_status, payment_price
#         orders = [
#             (1, 1, 1, 'COMPLETED', '2025-12-01 10:00:00', 'CARD', 'PAID', 15000),
#             (2, 2, 2, 'COMPLETED', '2025-12-02 11:00:00', 'BANK', 'PAID', 30000),
#         ]
#         cursor.executemany("""
#             INSERT INTO bg_order (id, user_id, address_id, order_status, ordered_at, payment_method, payment_status, payment_price)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#         """, orders)

#         # 6. 주문 상세 기록 생성 (실제 AI가 긁어가는 테이블)
#         try:
#             cursor.execute("DELETE FROM bg_order_item")
#             cursor.execute("DELETE FROM sqlite_sequence WHERE name='bg_order_item'")
            
#             # 데이터 형식을 (id, order_id, product_id, quantity, price) 5개로 맞춥니다.
#             order_items = [
#                 (1, 1, 101, 1, 15000), # 유저1이 101번 상품 1개를 15000원에 구매
#                 (2, 2, 103, 1, 30000), # 유저2가 103번 상품 1개를 30000원에 구매
#             ]
            
#             # 5개의 값을 넣으므로 ?도 5개를 씁니다.
#             cursor.executemany(
#                 "INSERT INTO bg_order_item (id, order_id, product_id, quantity, price) VALUES (?, ?, ?, ?, ?)", 
#                 order_items
#             )
            
#         except sqlite3.OperationalError as e:
#             self.stdout.write(self.style.WARNING(f"bg_order_item 테이블 작업 중 오류: {e}"))

#         # 최종 저장 및 종료
#         conn.commit()
#         conn.close()

#         self.stdout.write(self.style.SUCCESS("--- 테스트 데이터 삽입 완료! ---"))


import sqlite3
import random
from datetime import datetime
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = '유저 취향 그룹화를 적용하여 100명/500개 상품의 대규모 데이터를 생성합니다.'

    def handle(self, *args, **options):
        db_path = r"C:\AImy\Workspace\bogam\project.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        self.stdout.write("--- 기존 데이터 초기화 중 ---")
        tables = ['bg_user', 'bg_product', 'bg_cart', 'bg_wishlist', 'bg_recent_product', 'bg_review', 'bg_order', 'bg_order_item']
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
            except: pass

        # 1. 유저 생성 (100명)
        users = [(i, f'user{i}', '1234', f'테스터{i}', f'010-0000-{i:04d}', f'u{i}@test.com', '12345', '서울', '데이터구') for i in range(1, 101)]
        cursor.executemany("INSERT INTO bg_user (id, login_id, password, name, phone, email, zipcode, address, address_detail) VALUES (?,?,?,?,?,?,?,?,?)", users)

        # 2. 상품 생성 (500개)
        fruits = ['사과', '배', '포도', '딸기', '수박', '참외', '복숭아', '망고', '키위', '블루베리']
        products = []
        for i in range(1, 501):
            name = f"{random.choice(fruits)} {i}호"
            products.append((i, name, f"{name} 설명", random.randint(5000, 50000), 100, 'SALE', '국산'))
        cursor.executemany("INSERT INTO bg_product (id, product_name, content, price, stock, product_status, origin_name) VALUES (?,?,?,?,?,?,?)", products)

        # 3. 행동 데이터 생성 (취향 그룹화 로직)
        wish_data, cart_data, recent_data, review_data, orders, order_items = [], [], [], [], [], []
        o_id, oi_id = 1, 1

        for u_id in range(1, 101):
            # --- [핵심] 유저를 5개 취향 그룹으로 나눔 ---
            if u_id <= 20: p_range = range(1, 101)      # 1그룹: 1~100번 상품 선호
            elif u_id <= 40: p_range = range(101, 201)  # 2그룹: 101~200번 상품 선호
            elif u_id <= 60: p_range = range(201, 301)  # 3그룹: 201~300번 상품 선호
            elif u_id <= 80: p_range = range(301, 401)  # 4그룹: 301~400번 상품 선호
            else: p_range = range(401, 501)             # 5그룹: 401~500번 상품 선호

            # 그룹 내 선호 상품 20개 + 무작위 상품 5개 섞기
            target_products = random.sample(p_range, 20) + random.sample(range(1, 501), 5)
            
            for p_id in target_products:
                prob = random.random()
                # 최근 본 상품 (기본 활동)
                recent_data.append((u_id, p_id))
                
                # 찜 (취향이 강할 때)
                if prob < 0.5: wish_data.append((u_id, p_id))
                
                # 장바구니 (구매 의사)
                if prob < 0.3: cart_data.append((u_id, p_id, random.randint(1, 5)))
                
                # 리뷰 (점수 다양화: 1.0 ~ 5.0)
                if prob < 0.25:
                    # 취향 그룹 내 상품이면 높은 점수 줄 확률 업
                    rating = random.choices([1, 2, 3, 4, 5], weights=[1, 1, 2, 3, 5])[0]
                    review_data.append((p_id, u_id, "테스트 리뷰입니다.", float(rating)))

                # 주문 (가장 높은 가중치)
                if prob < 0.15:
                    orders.append((o_id, u_id, 1, 'COMPLETED', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'CARD', 'PAID', 25000))
                    order_items.append((oi_id, o_id, p_id, 1, 25000))
                    o_id += 1; oi_id += 1

        # 데이터 일괄 삽입
        self.stdout.write("--- 대량 데이터 주입 중... ---")
        cursor.executemany("INSERT INTO bg_wishlist (user_id, product_id) VALUES (?, ?)", wish_data)
        cursor.executemany("INSERT INTO bg_cart (user_id, product_id, quantity) VALUES (?, ?, ?)", cart_data)
        cursor.executemany("INSERT INTO bg_recent_product (user_id, product_id) VALUES (?, ?)", recent_data)
        cursor.executemany("INSERT INTO bg_review (product_id, user_id, content, rating) VALUES (?, ?, ?, ?)", review_data)
        cursor.executemany("INSERT INTO bg_order (id, user_id, address_id, order_status, ordered_at, payment_method, payment_status, payment_price) VALUES (?,?,?,?,?,?,?,?)", orders)
        
        try:
            cursor.executemany("INSERT INTO bg_order_item (id, order_id, product_id, quantity, price) VALUES (?, ?, ?, ?, ?)", order_items)
        except sqlite3.Error as e:
            self.stdout.write(self.style.WARNING(f"bg_order_item 삽입 에러(이미 존재할 수 있음): {e}"))

        conn.commit()
        conn.close()
        self.stdout.write(self.style.SUCCESS("--- 데이터 생성 완료! 이제 run_ai를 실행하여 추천 점수 분포를 확인하세요. ---"))