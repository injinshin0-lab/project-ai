from django.conf import settings

# --- [기초 정보 테이블] ---
from django.db.models.functions import Now
from django.db import models

# --- [1. 유저 정보 관련] ---
class Bg_User(models.Model):
    id = models.AutoField(primary_key=True)
    login_id = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=20, default='USER')
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())
    last_login_at = models.DateTimeField(null=True, blank=True)
    delivery_is_read = models.IntegerField(default=1)
    inquery_is_read = models.IntegerField(default=1)
    order_is_read = models.IntegerField(default=1)

    class Meta:
        managed = True
        db_table = 'bg_user'

class Bg_Address(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Bg_User, on_delete=models.CASCADE, db_column='user_id')
    recipient = models.CharField(max_length=255)
    postcode = models.CharField(max_length=20)
    address = models.CharField(max_length=500)
    detail_address = models.CharField(max_length=500)
    is_default = models.IntegerField(default=0)
    recipient_phone = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        managed = True
        db_table = 'bg_address'

class Bg_Alarm(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Bg_User, on_delete=models.CASCADE, db_column='user_id')
    type = models.CharField(max_length=50, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    is_read = models.IntegerField(default=0)

    class Meta:
        managed = True
        db_table = 'bg_alarm'

# --- [2. 상품 및 카테고리] ---
class Bg_Product(models.Model):
    id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    price = models.IntegerField()
    product_status = models.CharField(max_length=20, default='SALE')
    origin_name = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.CharField(max_length=500, null=True, blank=True)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        managed = True
        db_table = 'bg_product'


class Bg_Recent_product(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Bg_User, on_delete=models.CASCADE, db_column='user_id')
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE, db_column='product_id')
    viewed_at = models.DateTimeField(auto_now_add=True, db_default=Now())

    class Meta:
        managed = True
        db_table = 'bg_recent_product'


class Bg_Interest_category(models.Model):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, db_column='parent_id')
    depth = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'bg_interest_category'


class Bg_User_category_mapping(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Bg_User, on_delete=models.CASCADE, db_column='user_id')
    interest_category = models.ForeignKey(Bg_Interest_category, on_delete=models.CASCADE, db_column='interest_category_id')
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())

    class Meta:
        managed = True
        db_table = 'bg_user_category_mapping'


class Bg_Category_product_mapping(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE, db_column='product_id')
    interest_category = models.ForeignKey(Bg_Interest_category, on_delete=models.CASCADE, db_column='interest_category_id')

    class Meta:
        managed = True
        db_table = 'bg_category_product_mapping'

# --- [3. 주문 및 쇼핑 활동] ---
class Bg_Order(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Bg_User, on_delete=models.CASCADE, db_column='user_id')
    address = models.ForeignKey(Bg_Address, on_delete=models.CASCADE, db_column='address_id')
    order_status = models.CharField(max_length=50, default='PENDING')
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    payment_status = models.CharField(max_length=50, null=True, blank=True)
    payment_price = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())

    class Meta:
        managed = True
        db_table = 'bg_order'

class Bg_Order_item(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Bg_Order, on_delete=models.CASCADE, db_column='order_id')
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE, db_column='product_id')
    amount = models.IntegerField()
    price = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'bg_order_item'

class Bg_Cart(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Bg_User, on_delete=models.CASCADE, db_column='user_id')
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.IntegerField()
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'bg_cart'

class Bg_Wishlist(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Bg_User, on_delete=models.CASCADE, db_column='user_id')
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE, db_column='product_id')
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())

    class Meta:
        managed = True
        db_table = 'bg_wishlist'

# --- [4. 고객 지원 및 리뷰] ---
class Bg_FAQ(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        managed = True
        db_table = 'bg_faq'


class Bg_Question(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Bg_User, on_delete=models.CASCADE, db_column='user_id')
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE, null=True, blank=True, db_column='product_id')
    title = models.CharField(max_length=255)
    content = models.TextField()
    question_status = models.CharField(max_length=50, default='PENDING')
    type = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())

    class Meta:
        managed = True
        db_table = 'bg_question'

class Bg_Question_Image(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Bg_Question, on_delete=models.CASCADE, db_column='question_id')
    image_url = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())

    class Meta:
        managed = True
        db_table = 'bg_question_image'


class Bg_Answer(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Bg_Question, on_delete=models.CASCADE, db_column='question_id')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())

    class Meta:
        managed = True
        db_table = 'bg_answer'

class Bg_Review(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Bg_User, on_delete=models.CASCADE, db_column='user_id')
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE, db_column='product_id')
    content = models.TextField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        managed = True
        db_table = 'bg_review'


class Bg_Review_Image(models.Model):
    id = models.AutoField(primary_key=True)
    review = models.ForeignKey(Bg_Review, on_delete=models.CASCADE, db_column='review_id')
    image_url = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        managed = True
        db_table = 'bg_review_image'


# --- [5. AI 및 추천 관련] ---
class Bg_AI_recommendation(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Bg_User, on_delete=models.CASCADE, db_column='user_id')
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE, db_column='product_id')
    score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    expired_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'bg_ai_recommendation'

class Bg_Product_Similarity(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE, db_column='product_id')
    similar_product_id = models.IntegerField()
    similarity_score = models.FloatField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'bg_product_similarity'