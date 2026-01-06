from django.db import models

class Bg_Product(models.Model):
    product_name = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    image_url = models.CharField(max_length=500, null=True, blank=True)
    price = models.IntegerField() # 생성 앱에서는 price를 채워야 하므로 정의!

    class Meta:
        managed = False  # 어차피 project.db에 테이블은 있으니까요
        db_table = 'Bg_Product' # intelligence 모델과 같은 테이블을 바라봄

# 1. 유저 상세 (비밀번호, 이메일 등 포함)
class Bg_User_DataGen(models.Model):
    login_id = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    user_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=100)
    role = models.CharField(max_length=20, default='USER')

    class Meta:
        managed = False
        db_table = 'Bg_User'

# 2. 카테고리 상세 (부모 ID, 깊이 등 포함)
class Bg_Interest_category_DataGen(models.Model):
    category_name = models.CharField(max_length=100)
    parent_id = models.IntegerField(null=True, blank=True)
    depth = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'Bg_Interest_category'

# 3. 주문 상세 (상태값, 결제수단 등 포함)
class Bg_Order_DataGen(models.Model):
    user_id = models.IntegerField()
    address_id = models.IntegerField(null=True)
    order_status = models.CharField(max_length=20, default='COMPLETED')
    payment_method = models.CharField(max_length=20, default='CARD')
    payment_status = models.CharField(max_length=20, default='PAID')
    payment_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Bg_Order'

# 4. 주문 아이템
class Bg_Order_item_DataGen(models.Model):
    order_id = models.IntegerField()
    product_id = models.IntegerField()
    amount = models.IntegerField(default=1)
    price = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Bg_Order_item'

# 5. 행동 데이터 및 매핑 테이블들
class Bg_Wishlist_DataGen(models.Model):
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    class Meta: managed = False; db_table = 'Bg_Wishlist'

class Bg_Cart_DataGen(models.Model):
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    quantity = models.IntegerField(default=1)
    class Meta: managed = False; db_table = 'Bg_Cart'

class Bg_Recent_product_DataGen(models.Model):
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    class Meta: managed = False; db_table = 'Bg_Recent_product'

class Bg_Review_DataGen(models.Model):
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    content = models.TextField()
    rating = models.FloatField()
    class Meta: managed = False; db_table = 'Bg_Review'

class Bg_Category_product_mapping_DataGen(models.Model):
    product_id = models.IntegerField()
    interest_category_id = models.IntegerField()
    class Meta: managed = False; db_table = 'Bg_Category_product_mapping'

class Bg_User_category_mapping_DataGen(models.Model):
    user_id = models.IntegerField()
    interest_category_id = models.IntegerField()
    class Meta: managed = False; db_table = 'Bg_User_category_mapping'