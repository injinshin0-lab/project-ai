import os
import random
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from data_manager.models import Bg_Product

class Command(BaseCommand):
    help = '과일 종류에 맞는 원산지를 origin_name 컬럼에 삽입하여 상품 데이터를 생성합니다.'

    def handle(self, *args, **options):
        # 1. 기존 데이터 및 시퀀스 초기화
        self.stdout.write(self.style.WARNING('Bg_Product 데이터를 초기화 중...'))
        Bg_Product.objects.all().delete()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='Bg_Product';")

        # 2. 이미지 물리 경로 설정
        project_root = settings.BASE_DIR
        dataset_base_path = os.path.join(
            project_root.parent, "project-back", "uploads", "product", 
            "fruits-360-100x100-main", "Training"
        )

        if not os.path.exists(dataset_base_path):
            self.stdout.write(self.style.ERROR(f'경로를 찾을 수 없습니다: {dataset_base_path}'))
            return

        # 3. 매칭용 데이터 설정 (이 위치에 정의하면 Pylance 오류가 발생하지 않습니다)
        translation_table = {
            "Apple": "사과", "Apricot": "살구", "Avocado": "아보카도", "Banana": "바나나",
            "Beetroot": "비트", "Blueberry": "블루베리", "Cactus": "선인장열매", "Cantaloupe": "멜론",
            "Carambula": "스타프루트", "Carrot": "당근", "Cauliflower": "콜리플라워", "Cherry": "체리",
            "Chestnut": "밤", "Clementine": "클레멘타인", "Cocos": "코코넛", "Corn": "옥수수",
            "Cucumber": "오이", "Dates": "대추야자", "Eggplant": "가지", "Fig": "무화과",
            "Ginger": "생강", "Grape": "포도", "Grapefruit": "자몽", "Guava": "구아바",
            "Hazelnut": "헤이즐넛", "Kiwi": "키위", "Lemon": "레몬", "Lime": "라임",
            "Lychee": "리치", "Mandarine": "귤", "Mango": "망고", "Mangostan": "망고스틴",
            "Maracuja": "패션프루트", "Melon": "멜론", "Mulberry": "오디", "Nectarine": "천도복숭아",
            "Nut": "견과류", "Onion": "양파", "Orange": "오렌지", "Papaya": "파파야",
            "Peach": "복숭아", "Pear": "배", "Pepino": "페피노", "Pepper": "피망",
            "Pineapple": "파인애플", "Pistachio": "피스타치오", "Pitahaya": "용과", 
            "Plum": "자두", "Pomegranate": "석류", "Potato": "감자", "Raspberry": "산딸기",
            "Strawberry": "딸기", "Tomato": "토마토", "Walnut": "호두", "Watermelon": "수박"
        }

        # 과일 이름에 맞는 원산지 매칭 테이블
        origin_mapping = {
            "사과": ["충주", "청송", "의성", "문경"],
            "배": ["나주", "천안", "상주"],
            "귤": ["제주", "서귀포"],
            "포도": ["영동", "김천", "송산"],
            "복숭아": ["청도", "이천", "영덕"],
            "딸기": ["논산", "산청", "양평"],
            "수박": ["고창", "함안", "양평"],
            "감자": ["강원도", "평창", "제주"],
            "양파": ["무안", "창녕"],
            "자두": ["김천", "의성"],
            "밤": ["공주", "부여"],
            "호두": ["천안", "영동"]
        }

        default_locations = ["전국각지", "산지직송", "우리농가"]
        qualities = ["명품", "산지직송", "당도선별", "꿀", "유기농", "고랭지", "신선"]

        # 4. 데이터 추출 및 객체 생성
        classes = [d for d in os.listdir(dataset_base_path) if os.path.isdir(os.path.join(dataset_base_path, d))]
        new_products = []

        for class_name in classes:
            class_dir_path = os.path.join(dataset_base_path, class_name)
            files = [f for f in os.listdir(class_dir_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if not files: continue
            
            actual_file_name = files[0]

            # 한국어 이름 및 순수 과일명 추출
            kor_base_name = class_name
            pure_kor_name = "" 
            
            for eng, kor in translation_table.items():
                if eng in class_name:
                    variety = class_name.replace(eng, "").strip()
                    kor_base_name = f"{kor} ({variety})" if variety else kor
                    pure_kor_name = kor # 매칭을 위한 핵심 키워드
                    break
            
            # [핵심] 제목에 맞는 원산지를 선택하여 origin 변수에 저장
            if pure_kor_name in origin_mapping:
                origin = random.choice(origin_mapping[pure_kor_name])
            else:
                origin = random.choice(default_locations)
            
            # [핵심] 테이블 속성에 맞춰 데이터 매칭
            new_products.append(Bg_Product(
                product_name=f"[{origin}] {random.choice(qualities)} {kor_base_name}", # 제목에 포함
                origin_name=origin,   # <--- CREATE TABLE의 "origin_name" 컬럼에 삽입
                price=random.randint(5, 50) * 1000,
                image_url=f"product/fruits-360-100x100-main/Training/{class_name}/{actual_file_name}",
                content=f"{origin} 산지에서 직송된 신선한 {kor_base_name}입니다.",
                product_status='SALE'
            ))

        # 5. DB 일괄 삽입
        created_objs = Bg_Product.objects.bulk_create(new_products)
        self.stdout.write(self.style.SUCCESS(f'성공: {len(created_objs)}개의 데이터가 origin_name 필드와 함께 생성되었습니다.'))