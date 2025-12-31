import sqlite3
import random
from datetime import datetime
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = '상세 카테고리 태그 시스템을 포함한 대규모 테스트 데이터를 생성합니다.'

    def handle(self, *args, **options):
        db_path = r"C:\AImy\Workspace\bogam\project.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        self.stdout.write("--- 기존 데이터 초기화 중 ---")
        # 초기화할 테이블 목록 확장
        tables = [
            'bg_user', 'bg_product', 'bg_cart', 'bg_wishlist', 'bg_recent_product', 
            'bg_review', 'bg_order', 'bg_order_item', 'bg_interest_category', 
            'bg_category_product_mapping', 'bg_user_category_mapping'
        ]
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
            except: pass

        # 1. 상세 카테고리 리스트 생성 (124개)
        category_names = [
            "뷰티/피부 케어", "바디/운동", "건강 관리", "식습관/식단", "정신/웰니스",
            "미백/톤업", "수분/촉촉", "탄력/동안", "붓기 완화", "근육 생성",
            "운동 에너지", "운동 후 회복", "체중 관리", "소화/위 건강", "면역력/감기",
            "눈 건강", "만성피로", "저탄수화물", "비건/채식", "식감 중심",
            "간편한 식사", "스트레스 완화", "집중력 향상", "감정 안정", "활력/기분전환",
            "비타민C 고함량", "멜라닌 억제", "피부 미백 항산화", "피부 정화", "피부 컨디션 회복",
            "수분 가득", "히알루론산 식품", "수분 유지", "피부 진정", "수분 손실 방지",
            "콜라겐 합성 도움", "비타민E 풍부", "피부 장벽 강화", "노화 방지", "피부 재생",
            "칼륨 풍부", "수분 배출", "순환 개선", "염분 조절", "림프 순환",
            "근육 생성 단백질", "아미노산 공급", "근육 회복", "철분 보충", "고단백 견과",
            "저GI 탄수", "빠른 에너지", "지구력 강화", "운동 활력 항산화", "미량 영양소",
            "근육 통증 완화", "피로 회복", "전해질 보충", "운동 후 항염", "수분 회복",
            "저칼로리", "체중 관리 식이섬유", "포만감", "수분 채움", "지방 대사 도움",
            "속 편한 식품", "소화 효소", "장 운동 촉진", "장내 환경 개선", "위 보호",
            "비타민C 보강", "기관지/면역 항염", "항바이러스", "면역 부스팅", "목 관리",
            "루테인", "베타카로틴", "안구 건조 완화", "블루라이트 보호", "피로 눈 완화",
            "피로회복", "철분·혈액순환", "혈당 안정", "피로 해소 비타민B", "피로 유발 스트레스 완화",
            "저당 과일", "저탄수 채소", "대체 탄수", "혈당관리", "단백질·지방 대체",
            "비건용 단백질", "비건 간식", "비건 식이섬유", "비타민 보충", "비건 철분",
            "아삭함", "쫄깃함", "부드러움", "크런치", "씹는 맛",
            "즉석 과일", "즉석 샐러드", "즉석 스팀 채소", "즉석 곡물", "한 끼 대용",
            "마그네슘", "진정 효과", "긴장 완화", "스트레스 케어 항산화", "숙면 도움",
            "뇌 에너지", "오메가-3", "두뇌 활성 항산화", "혈류 개선", "두뇌 집중 비타민B",
            "세로토닌 증가", "정서적 스트레스 완화", "진정 허브", "피로 감소", "심신 안정 항염",
            "활력 보충 비타민C", "엔도르핀 도움", "에너지 공급", "가벼운 활력", "기분 전환 항산화"
        ]
        
        cats = [(i, name, None, 1) for i, name in enumerate(category_names, 1)]
        cursor.executemany("INSERT INTO bg_interest_category (id, category_name, parent_id, depth) VALUES (?,?,?,?)", cats)

        # 2. 유저 생성 (100명)
        users = [(i, f'user{i}', '1234', f'테스터{i}', f'010-0000-{i:04d}', f'u{i}@test.com', '12345', '서울', '데이터구') for i in range(1, 101)]
        cursor.executemany("INSERT INTO bg_user (id, login_id, password, name, phone, email, zipcode, address, address_detail) VALUES (?,?,?,?,?,?,?,?,?)", users)

        # 3. 상품 생성 (500개)
        fruits = ['사과', '배', '포도', '딸기', '수박', '참외', '복숭아', '망고', '키위', '블루베리']
        products = []
        for i in range(1, 501):
            name = f"{random.choice(fruits)} {i}호"
            products.append((i, name, f"{name} 설명", random.randint(5000, 50000), 100, 'SALE', '국산'))
        cursor.executemany("INSERT INTO bg_product (id, product_name, content, price, stock, product_status, origin_name) VALUES (?,?,?,?,?,?,?)", products)

        # 4. 상품-카테고리 매핑 (상품당 1~3개)
        prod_cat_map = []
        for p_id in range(1, 501):
            chosen = random.sample(range(1, len(category_names) + 1), random.randint(1, 3))
            for c_id in chosen:
                prod_cat_map.append((p_id, c_id))
        cursor.executemany("INSERT INTO bg_category_product_mapping (product_id, interest_category_id) VALUES (?,?)", prod_cat_map)

        # 5. 유저 관심사 매핑 (유저당 2~5개)
        user_int_map = []
        for u_id in range(1, 101):
            chosen = random.sample(range(1, len(category_names) + 1), random.randint(2, 5))
            for c_id in chosen:
                user_int_map.append((u_id, c_id))
        cursor.executemany("INSERT INTO bg_user_category_mapping (user_id, interest_category_id) VALUES (?,?)", user_int_map)

        # 6. 행동 데이터 생성 (유저 취향 그룹화 유지)
        wish_data, cart_data, recent_data, review_data, orders, order_items = [], [], [], [], [], []
        o_id, oi_id = 1, 1

        for u_id in range(1, 101):
            # 그룹화 로직
            if u_id <= 20: p_range = range(1, 101)
            elif u_id <= 40: p_range = range(101, 201)
            elif u_id <= 60: p_range = range(201, 301)
            elif u_id <= 80: p_range = range(301, 401)
            else: p_range = range(401, 501)

            target_products = random.sample(p_range, 15) + random.sample(range(1, 501), 3)
            
            for p_id in target_products:
                prob = random.random()
                recent_data.append((u_id, p_id))
                if prob < 0.4: wish_data.append((u_id, p_id))
                if prob < 0.2: cart_data.append((u_id, p_id, 1))
                if prob < 0.1:
                    rating = random.choices([3, 4, 5], weights=[2, 3, 5])[0]
                    review_data.append((p_id, u_id, "좋아요!", float(rating)))
                    orders.append((o_id, u_id, 1, 'COMPLETED', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'CARD', 'PAID', 10000))
                    order_items.append((oi_id, o_id, p_id, 1, 10000))
                    o_id += 1; oi_id += 1

        # 일괄 삽입
        cursor.executemany("INSERT INTO bg_wishlist (user_id, product_id) VALUES (?, ?)", wish_data)
        cursor.executemany("INSERT INTO bg_cart (user_id, product_id, quantity) VALUES (?, ?, ?)", cart_data)
        cursor.executemany("INSERT INTO bg_recent_product (user_id, product_id) VALUES (?, ?)", recent_data)
        cursor.executemany("INSERT INTO bg_review (product_id, user_id, content, rating) VALUES (?, ?, ?, ?)", review_data)
        cursor.executemany("INSERT INTO bg_order (id, user_id, address_id, order_status, ordered_at, payment_method, payment_status, payment_price) VALUES (?,?,?,?,?,?,?,?)", orders)
        cursor.executemany("INSERT INTO bg_order_item (id, order_id, product_id, quantity, price) VALUES (?, ?, ?, ?, ?)", order_items)

        conn.commit()
        conn.close()
        self.stdout.write(self.style.SUCCESS(f"--- 데이터 생성 완료! 카테고리 {len(category_names)}개 포함 ---"))