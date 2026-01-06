import sqlite3
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = '관심 카테고리 가산점을 적용하여 대량의 유저 행동 데이터를 생성합니다.'

    def handle(self, *args, **options):
        db_path = str(settings.DATABASES['default']['NAME'])
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        self.stdout.write("--- 유저 및 행동 데이터 빅데이터 생성 시작 ---")

        # 1. 초기화 (기존 데이터 삭제)
        tables = ['Bg_User', 'Bg_User_category_mapping', 'Bg_Recent_product', 
                  'Bg_Wishlist', 'Bg_Cart', 'Bg_Order', 'Bg_Order_item', 'Bg_Review']
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
            except: pass

        # 2. 유저 100명 생성
        users = []
        for i in range(1, 101):
            users.append((i, f'user{i}', '1234', f'테스터{i}', f'010-0000-{i:04d}', f'u{i}@test.com', 'USER'))
        
        cursor.executemany("""
            INSERT INTO Bg_User (id, login_id, password, user_name, phone, email, role) 
            VALUES (?,?,?,?,?,?,?)
        """, users)

        # 3. 유저별 관심 카테고리 매핑
        cursor.execute("SELECT id FROM Bg_Interest_category WHERE depth=3")
        all_small_cats = [row[0] for row in cursor.fetchall()]
        
        user_interests = {}
        user_cat_map = []
        for u_id in range(1, 101):
            chosen = random.sample(all_small_cats, random.randint(3, 5))
            user_interests[u_id] = chosen
            for c_id in chosen:
                user_cat_map.append((u_id, c_id))
        cursor.executemany("INSERT INTO Bg_User_category_mapping (user_id, interest_category_id) VALUES (?,?)", user_cat_map)

        # 4. 카테고리/상품 리스트 로드
        cursor.execute("SELECT product_id, interest_category_id FROM Bg_Category_product_mapping")
        cat_prod_dict = {}
        for p_id, c_id in cursor.fetchall():
            if c_id not in cat_prod_dict: cat_prod_dict[c_id] = []
            cat_prod_dict[c_id].append(p_id)

        cursor.execute("SELECT id FROM Bg_Product")
        all_product_ids = [row[0] for row in cursor.fetchall()]

        # 5. 행동 데이터 대량 생성 (주문 및 장바구니)
        o_id, oi_id = 1, 1
        now = datetime.now()

        for _ in range(10000):
            u_id = random.randint(1, 100)
            if random.random() < 0.7:
                target_cat = random.choice(user_interests[u_id])
                target_p_id = random.choice(cat_prod_dict.get(target_cat, all_product_ids))
            else:
                target_p_id = random.choice(all_product_ids)

            cursor.execute("INSERT OR IGNORE INTO Bg_Cart (user_id, product_id, quantity) VALUES (?,?,?)", (u_id, target_p_id, 1))

            created_at = (now - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                INSERT INTO Bg_Order (id, user_id, address_id, order_status, payment_method, payment_status, payment_price, created_at) 
                VALUES (?,?,?,?,?,?,?,?)
            """, (o_id, u_id, 1, 'COMPLETED', 'CARD', 'PAID', 15000, created_at))
            
            cursor.execute("""
                INSERT INTO Bg_Order_item (id, order_id, product_id, amount, price) 
                VALUES (?,?,?,?,?)
            """, (oi_id, o_id, target_p_id, 1, 15000))
            
            o_id += 1
            oi_id += 1

        # 6. 추가 행동 데이터 (찜하기 1.5만건, 최근 본 상품 2만건)
        for action, count in [('Wishlist', 15000), ('Recent', 20000)]:
            data_list = []
            for _ in range(count):
                u_id = random.randint(1, 100)
                if random.random() < 0.7:
                    target_cat = random.choice(user_interests[u_id])
                    target_p_id = random.choice(cat_prod_dict.get(target_cat, all_product_ids))
                else:
                    target_p_id = random.choice(all_product_ids)
                data_list.append((u_id, target_p_id))
            
            table_name = 'Bg_Wishlist' if action == 'Wishlist' else 'Bg_Recent_product'
            cursor.executemany(f"INSERT OR IGNORE INTO {table_name} (user_id, product_id) VALUES (?,?)", data_list)

        # [중요] 7. 저장 및 종료
        conn.commit()
        conn.close()
        self.stdout.write(self.style.SUCCESS(f"성공: 주문 10,000건 및 행동 데이터 약 4만 건 생성이 완료되었습니다."))