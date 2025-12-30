import random
import sqlite3
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from intelligence.models import (
    Bg_Product, Bg_Wishlist, Bg_Order_Item, 
    Bg_Cart, Bg_Recent_product, Bg_Review
)

class Command(BaseCommand):
    help = '외부 DB 상품 기반으로 가짜 활동 데이터 생성'

    def handle(self, *args, **kwargs):
        self.stdout.write("외부 DB로부터 상품을 동기화하고 가짜 데이터를 생성합니다...")

        # 1. 외부 DB(aiprojectdb.db)에서 진짜 상품명 가져오기
        db_path = os.path.join(settings.BASE_DIR, 'aiprojectdb.db')
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f"파일 없음: {db_path}"))
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM product") # 외부 DB의 상품명 컬럼
        external_item_names = [row[0] for row in cursor.fetchall()]
        conn.close()

        # 2. 우리 DB(Bg_Product)에 등록 및 리스트 확보
        products = []
        for name in external_item_names:
            product, _ = Bg_Product.objects.get_or_create(name=name)
            products.append(product)

        if not products:
            self.stdout.write(self.style.ERROR("외부 DB에 상품이 하나도 없습니다."))
            return

        # 3. 유저 10명 확보
        users = [User.objects.get_or_create(username=f'user_{i}')[0] for i in range(1, 11)]

        # 4. 이제 이 '진짜 상품'들을 대상으로 랜덤 행동 생성
        actions = [
            (Bg_Order_Item, 50),   # 주문 50건
            (Bg_Wishlist, 70),     # 찜 70건
            (Bg_Cart, 60),         # 장바구니 60건
            (Bg_Recent_product, 100) # 최근 본 상품 100건
        ]

        for model, repeat_count in actions:
            count = 0
            while count < repeat_count:
                u = random.choice(users)
                p = random.choice(products) # 외부 DB에서 온 상품들 중 선택
                obj, created = model.objects.get_or_create(user=u, product=p)
                if created: count += 1

        # 5. 리뷰 데이터 (1~5점 랜덤)
        review_count = 0
        while review_count < 50:
            u = random.choice(users)
            p = random.choice(products)
            obj, created = Bg_Review.objects.get_or_create(
                user=u, product=p, 
                defaults={'rating': random.randint(1, 5)}
            )
            if created: review_count += 1

        self.stdout.write(self.style.SUCCESS(f'성공: 외부 DB의 {len(products)}개 상품을 기반으로 가짜 데이터 생성 완료!'))