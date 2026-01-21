from django.db import models
from django.conf import settings


# --- [기초 정보 테이블] ---

from django.db import models

# --- [1. 유저 정보] ---
class Bg_User(models.Model):
    # 실제 컬럼명: id, login_id, user_name 등 
    login_id = models.CharField(max_length=150, unique=True) # 
    user_name = models.CharField(max_length=150)             # 

    class Meta:
        managed = False      # DB 담당자가 관리하므로 읽기 전용 
        db_table = 'Bg_User'

# --- [2. 상품 및 카테고리] ---
class Bg_Product(models.Model):
    # 실제 컬럼명: product_name (name 아님), content, image_url 등 
    product_name = models.CharField(max_length=255) # 
    content = models.TextField(null=True, blank=True) # 
    image_url = models.CharField(max_length=500, null=True, blank=True) # 

    class Meta:
        managed = False
        db_table = 'Bg_Product'

class Bg_Interest_category(models.Model):
    # 실제 컬럼명: category_name 
    category_name = models.CharField(max_length=255) # 

    class Meta:
        managed = False
        db_table = 'Bg_Interest_category'

class Bg_User_category_mapping(models.Model):
    user = models.ForeignKey(Bg_User, on_delete=models.DO_NOTHING, db_column='user_id')
    interest_category = models.ForeignKey(Bg_Interest_category, on_delete=models.DO_NOTHING, db_column='interest_category_id')

    class Meta:
        managed = False
        db_table = 'Bg_User_category_mapping' # 실제 DB 테이블명

# 상품-카테고리 매핑 테이블
class Bg_Category_product_mapping(models.Model):
    product = models.ForeignKey(Bg_Product, on_delete=models.DO_NOTHING, db_column='product_id')
    interest_category = models.ForeignKey(Bg_Interest_category, on_delete=models.DO_NOTHING, db_column='interest_category_id')

    class Meta:
        managed = False
        db_table = 'Bg_Category_product_mapping'

# --- [3. 유저 행동 데이터 (AI 분석 핵심)] ---
class Bg_Order(models.Model):
    user = models.ForeignKey(Bg_User, on_delete=models.DO_NOTHING, db_column='user_id')

    class Meta:
        managed = False
        db_table = 'Bg_Order' #
        
class Bg_Order_item(models.Model):
    order = models.ForeignKey(Bg_Order, on_delete=models.DO_NOTHING, db_column='order_id')
    product = models.ForeignKey(Bg_Product, on_delete=models.DO_NOTHING, db_column='product_id')

    class Meta:
        managed = False
        db_table = 'Bg_Order_item' # [cite: 520, 521]

class Bg_Review(models.Model):
    user = models.ForeignKey(Bg_User, on_delete=models.DO_NOTHING, db_column='user_id')
    product = models.ForeignKey(Bg_Product, on_delete=models.DO_NOTHING, db_column='product_id')
    rating = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Bg_Review'

class Bg_Wishlist(models.Model):
    user = models.ForeignKey(Bg_User, on_delete=models.DO_NOTHING, db_column='user_id')
    product = models.ForeignKey(Bg_Product, on_delete=models.DO_NOTHING, db_column='product_id')

    class Meta:
        managed = False
        db_table = 'Bg_Wishlist'

class Bg_Recent_product(models.Model):
    user = models.ForeignKey(Bg_User, on_delete=models.DO_NOTHING, db_column='user_id')
    product = models.ForeignKey(Bg_Product, on_delete=models.DO_NOTHING, db_column='product_id')

    class Meta:
        managed = False
        db_table = 'Bg_Recent_product'

class Bg_Cart(models.Model):
    user = models.ForeignKey(Bg_User, on_delete=models.DO_NOTHING, db_column='user_id')
    product = models.ForeignKey(Bg_Product, on_delete=models.DO_NOTHING, db_column='product_id')

    class Meta:
        managed = False
        db_table = 'Bg_Cart'

# --- [4. AI 분석 결과 저장] ---
class Bg_AI_recommendation(models.Model):
    user = models.ForeignKey(Bg_User, on_delete=models.DO_NOTHING, db_column='user_id')
    product = models.ForeignKey(Bg_Product, on_delete=models.DO_NOTHING, db_column='product_id')
    score = models.FloatField()

    class Meta:
        managed = False
        db_table = 'Bg_AI_recommendation'