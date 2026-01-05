from django.db import models
from django.conf import settings


# --- [기초 정보 테이블] ---

# 1. 상품 테이블
class Bg_Product(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        db_table = 'Bg_Product'
    
# 2. 카테고리 정보 테이블
class Bg_Category(models.Model):
    name = models.CharField(max_length=255)
    # 신규 필드 추가 
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    depth = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'Bg_Interest_category'

# 3. 상품-카테고리 매핑
class Bg_Product_Category_Mapping(models.Model):
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Bg_Category, on_delete=models.CASCADE)
    class Meta:
        db_table = 'Bg_Category_product_mapping'
        unique_together = ('product', 'category')

# 4. 리뷰
class Bg_Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE)
    rating = models.FloatField()
    class Meta:
        db_table = 'Bg_Review'

# 5. 장바구니
class Bg_Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1) # 수량 정보 추가
    class Meta:
        db_table = 'Bg_Cart'

# 6. 최근 본 상품
class Bg_Recent_product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'Bg_Recent_product'

# 7. 찜 (Wishlist)
class Bg_Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE)
    class Meta:
        db_table = 'Bg_Wishlist'

# 8. 주문 상품
class Bg_Order_Item(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE)
    class Meta:
        db_table = 'Bg_Order_Item'

# 9. 사용자 관심분야 등록
class Bg_User_interest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    interest_category_id = models.IntegerField()
    class Meta:
        db_table = 'Bg_User_category_mapping'

# --- [AI 분석 결과 테이블] ---

# 10. 사용자별 AI 추천 결과
class BgAiRecommendation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        db_column='user_id'
    )
    product = models.ForeignKey(
        Bg_Product, 
        on_delete=models.CASCADE, 
        db_column='product_id'
    )
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Bg_AI_recommendation'
        unique_together = ('user', 'product')