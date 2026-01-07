import os
import random
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from data_manager.models import Bg_Product

class Command(BaseCommand):
    help = 'bogam/fruits-360-100x100-main/Training 경로를 읽어 상품 데이터를 생성합니다.'

    def handle(self, *args, **options):
        # 1. 기존 데이터 초기화
        self.stdout.write(self.style.WARNING('Bg_Product 데이터를 초기화 중...'))
        Bg_Product.objects.all().delete()
        
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='Bg_Product';")

        # 2. 알려주신 구조로 경로 수정
        # bogam/project-back/uploads/product/fruits-360-100x100-main/Training
        project_root = settings.BASE_DIR  # project-ai 위치
        
        dataset_base_path = os.path.join(
            project_root.parent,            # bogam 폴더로 이동
            "project-back",                 # project-back 폴더 진입
            "uploads",                      # uploads 폴더 진입
            "product",                      # product 폴더 진입
            "fruits-360-100x100-main",      # 이미지 데이터셋 루트
            "Training"                      # 실제 이미지들이 있는 폴더
        )

        if not os.path.exists(dataset_base_path):
            self.stdout.write(self.style.ERROR(f'여전히 경로를 찾을 수 없습니다: {dataset_base_path}'))
            self.stdout.write('폴더명을 다시 한번 확인해주세요.')
            return

        # 3. 번역 및 수식어 설정 (이전과 동일)
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
        locations = ["충주", "청송", "영동", "나주", "제주", "무안", "해남", "의성", "문경", "상주", "성주"]
        qualities = ["명품", "산지직송", "당도선별", "꿀", "유기농", "고랭지", "신선"]

        # 4. 데이터 생성 및 삽입
        classes = [d for d in os.listdir(dataset_base_path) if os.path.isdir(os.path.join(dataset_base_path, d))]

        new_products = []
        for class_name in classes:
            kor_base = class_name
            for eng, kor in translation_table.items():
                if eng in class_name:
                    variety = class_name.replace(eng, "").strip()
                    kor_base = f"{kor} ({variety})" if variety else kor
                    break
            
            p_name = f"{random.choice(locations)} {random.choice(qualities)} {kor_base}"
            image_url = f"fruits-360-100x100-main/Training/{class_name}/0_100.jpg"
            
            # [수정됨] 모델의 실제 필드명과 일치시킴
            new_products.append(Bg_Product(
                product_name=p_name,  # name -> product_name
                price=random.randint(5, 50) * 1000,
                image_url=image_url,
                content=f"신선한 {kor_base}입니다. 산지에서 직접 배송해 드립니다."
                # origin_name은 현재 모델에 없으므로 제외하거나 models.py에 추가 후 사용하세요.
            ))

        created_objs = Bg_Product.objects.bulk_create(new_products)
        self.stdout.write(self.style.SUCCESS(f'성공: {len(created_objs)}개의 상품이 실제 생성되었습니다.'))