import sqlite3
import random
from datetime import datetime
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = '변경된 DB 스키마를 반영하여 대규모 테스트 데이터를 생성합니다.'

    def handle(self, *args, **options):
        # 0. 경로 설정 (사용자님의 환경에 맞춤)
        db_path = r"C:\AImy\Workspace\bogam\project.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        self.stdout.write("--- 최신 스키마 기준 기존 데이터 초기화 중 ---")
        
        # [수정 1] 테이블명을 PascalCase 스키마와 동일하게 수정
        tables = [
            'Bg_User', 'Bg_Product', 'Bg_Cart', 'Bg_Wishlist', 'Bg_Recent_product', 
            'Bg_Review', 'Bg_Order', 'Bg_Order_item', 'Bg_Interest_category', 
            'Bg_Category_product_mapping', 'Bg_User_category_mapping', 'Bg_AI_recommendation'
        ]
        
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
            except: pass

        # 1. 상세 카테고리 생성
        category_names = [
            "뷰티/피부 케어", "바디/운동", "건강 관리", "식습관/식단", "정신/웰니스",
            "미백/톤업", "수분/촉촉", "탄력/동안", "붓기 완화", "근육 생성"
            # ... (나머지 카테고리 이름들은 유지)
        ]
        
        # [수정 2] Bg_Interest_category (id, category_name, parent_id, depth)
        cats = [(i, name, None, 1) for i, name in enumerate(category_names, 1)]
        cursor.executemany("INSERT INTO Bg_Interest_category (id, category_name, parent_id, depth) VALUES (?,?,?,?)", cats)

        # 2. 유저 생성 (100명)
        # [수정 3] Bg_User 컬럼명 변경 반영: name -> user_name, zipcode -> postcode
        # 스키마 순서: id, login_id, password, user_name, phone, email, role, status
        users = []
        for i in range(1, 101):
            users.append((i, f'user{i}', '1234', f'테스터{i}', f'010-0000-{i:04d}', f'u{i}@test.com', 'USER'))
        cursor.executemany(
            "INSERT INTO Bg_User (id, login_id, password, user_name, phone, email, role) VALUES (?,?,?,?,?,?,?)", 
            users
        )

        # 3. 상품 생성 (500개)
        # [수정 4] Bg_Product (id, product_name, content, price, stock, product_status, origin_name)
        fruits = ['사과', '배', '포도', '딸기', '수박', '참외', '복숭아', '망고', '키위', '블루베리']
        products = []
        for i in range(1, 501):
            name = f"{random.choice(fruits)} {i}호"
            products.append((i, name, f"{name} 설명", random.randint(5000, 50000), 100, 'SALE', '국산'))
        cursor.executemany("INSERT INTO Bg_Product (id, product_name, content, price, stock, product_status, origin_name) VALUES (?,?,?,?,?,?,?)", products)

        # 4. 상품-카테고리 매핑
        # [수정 5] Bg_Category_product_mapping (product_id, interest_category_id)
        prod_cat_map = []
        for p_id in range(1, 501):
            chosen = random.sample(range(1, len(category_names) + 1), random.randint(1, 3))
            for c_id in chosen:
                prod_cat_map.append((p_id, c_id))
        cursor.executemany("INSERT INTO Bg_Category_product_mapping (product_id, interest_category_id) VALUES (?,?)", prod_cat_map)

        # 5. 유저 관심사 매핑
        # [수정 6] Bg_User_category_mapping (user_id, interest_category_id)
        user_int_map = []
        for u_id in range(1, 101):
            chosen = random.sample(range(1, len(category_names) + 1), random.randint(2, 5))
            for c_id in chosen:
                user_int_map.append((u_id, c_id))
        cursor.executemany("INSERT INTO Bg_User_category_mapping (user_id, interest_category_id) VALUES (?,?)", user_int_map)

        # 6. 행동 데이터 생성
        wish_data, cart_data, recent_data, review_data, orders, order_items = [], [], [], [], [], []
        o_id, oi_id = 1, 1
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for u_id in range(1, 101):
            # 그룹별 상품 범위 설정
            if u_id <= 20: p_range = range(1, 41)
            elif u_id <= 40: p_range = range(41, 81)
            elif u_id <= 60: p_range = range(81, 121)
            elif u_id <= 80: p_range = range(121, 161)
            else: p_range = range(161, 201)

            target_products = random.sample(p_range, 25)
            
            for p_id in target_products:
                prob = random.random()
                recent_data.append((u_id, p_id))
                
                if prob < 0.8: # 찜
                    wish_data.append((u_id, p_id))
                
                if prob < 0.6: # 장바구니
                    cart_data.append((u_id, p_id, 1))
                
                if prob < 0.4: # 리뷰 및 주문
                    rating = round(random.uniform(3.0, 5.0), 2)
                    review_data.append((u_id, p_id, "추천합니다!", rating))
                    
                    # [수정 7] Bg_Order (id, user_id, address_id, order_status, payment_method, payment_status, payment_price, created_at)
                    # 주소 데이터가 없으므로 임의의 address_id 1번 사용
                    orders.append((o_id, u_id, 1, 'COMPLETED', 'CARD', 'PAID', 10000, now_str))
                    # [수정 8] Bg_Order_item (id, order_id, product_id, amount, price)
                    order_items.append((oi_id, o_id, p_id, 1, 10000))
                    o_id += 1
                    oi_id += 1

        # 일괄 삽입 (테이블명 PascalCase 반영)
        cursor.executemany("INSERT INTO Bg_Wishlist (user_id, product_id) VALUES (?, ?)", wish_data)
        cursor.executemany("INSERT INTO Bg_Cart (user_id, product_id, quantity) VALUES (?, ?, ?)", cart_data)
        cursor.executemany("INSERT INTO Bg_Recent_product (user_id, product_id) VALUES (?, ?)", recent_data)
        cursor.executemany("INSERT INTO Bg_Review (user_id, product_id, content, rating) VALUES (?, ?, ?, ?)", review_data)
        cursor.executemany("INSERT INTO Bg_Order (id, user_id, address_id, order_status, payment_method, payment_status, payment_price, created_at) VALUES (?,?,?,?,?,?,?,?)", orders)
        cursor.executemany("INSERT INTO Bg_Order_item (id, order_id, product_id, amount, price) VALUES (?, ?, ?, ?, ?)", order_items)

        conn.commit()
        conn.close()
        self.stdout.write(self.style.SUCCESS(f"--- 데이터 생성 완료! ---"))