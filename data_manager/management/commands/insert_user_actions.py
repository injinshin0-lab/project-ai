import sqlite3
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = '유저, 주소, 행동 데이터를 생성하며 100번 유저를 관리자로 설정합니다.'

    def handle(self, *args, **options):
        db_path = str(settings.DATABASES['default']['NAME'])
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        self.stdout.write("--- 유저(100번 관리자 포함), 주소 및 행동 데이터 생성 시작 ---")

        # 1. 초기화
        tables = ['Bg_User', 'Bg_User_category_mapping', 'Bg_Recent_product', 
                  'Bg_Wishlist', 'Bg_Cart', 'Bg_Order', 'Bg_Order_item', 'Bg_Review', 'Bg_Address']
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
            except: pass

        # 2. 유저 100명 생성 (100번은 관리자)
        users = []
        for i in range(1, 101):
            if i == 100:
                # 100번 유저: 관리자 설정
                users.append((i, 'admin', '1234', '관리자', '010-0000-0100', 'admin@test.com', 'ADMIN'))
            else:
                # 1~99번 유저: 일반 유저
                users.append((i, f'user{i}', '1234', f'테스터{i}', f'010-0000-{i:04d}', f'u{i}@test.com', 'USER'))
        
        cursor.executemany("""
            INSERT INTO Bg_User (id, login_id, password, user_name, phone, email, role) 
            VALUES (?,?,?,?,?,?,?)
        """, users)

        # 3. 유저별 주소(Bg_Address) 생성
        cities = ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시", "세종특별자치시"]
        provinces = ["경기도 수원시", "강원도 춘천시", "충청북도 청주시", "전라남도 목포시", "경상북도 포항시", "제주특별자치도 제주시"]
        all_regions = cities + provinces
        
        addresses = []
        user_to_address = {}
        
        for i in range(1, 101):
            addr_id = i
            base_addr = random.choice(all_regions)
            full_addr = f"{base_addr} {random.randint(1, 100)}-{random.randint(1, 50)}"
            detail = f"{random.randint(101, 999)}동 {random.randint(101, 2000)}호"
            postcode = f"{random.randint(10000, 99999):05d}"
            phone = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            
            # 관리자(100번)도 배송지 1개는 기본적으로 생성해둡니다.
            recipient_name = "관리자" if i == 100 else f"수령인 test {i}"
            addresses.append((addr_id, i, recipient_name, postcode, full_addr, detail, 1, phone))
            user_to_address[i] = addr_id

        cursor.executemany("""
            INSERT INTO Bg_Address (id, user_id, recipient, postcode, address, detail_address, is_default, recipient_phone)
            VALUES (?,?,?,?,?,?,?,?)
        """, addresses)

        # 4. 유저별 관심 카테고리 매핑
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

        # 5. 상품 데이터 로드
        cursor.execute("SELECT product_id, interest_category_id FROM Bg_Category_product_mapping")
        cat_prod_dict = {}
        for p_id, c_id in cursor.fetchall():
            if c_id not in cat_prod_dict: cat_prod_dict[c_id] = []
            cat_prod_dict[c_id].append(p_id)

        cursor.execute("SELECT id FROM Bg_Product")
        all_product_ids = [row[0] for row in cursor.fetchall()]

        # 6. 행동 데이터 및 주문 생성
        o_id, oi_id = 1, 1
        now = datetime.now()

        for _ in range(10000):
            u_id = random.randint(1, 100)
            assigned_addr_id = user_to_address[u_id]
            
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
            """, (o_id, u_id, assigned_addr_id, 'COMPLETED', 'CARD', 'PAID', 15000, created_at))
            
            cursor.execute("""
                INSERT INTO Bg_Order_item (id, order_id, product_id, amount, price) 
                VALUES (?,?,?,?,?)
            """, (oi_id, o_id, target_p_id, 1, 15000))
            
            o_id += 1
            oi_id += 1

        # 7. 추가 행동 데이터
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

        conn.commit()
        conn.close()
        self.stdout.write(self.style.SUCCESS("성공: 100번 관리자 계정 생성 및 전체 데이터 매칭이 완료되었습니다."))