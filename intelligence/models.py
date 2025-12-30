from django.db import models
from django.conf import settings


# --- [기초 정보 테이블] ---

# 1. 임시 상품 테이블
class Bg_Product(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        db_table = 'Bg_Product'

# 2. 소분류 카테고리 매핑 (관심분야)
class Bg_Category_product(models.Model):
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE)
    interest_category_id = models.IntegerField()
    class Meta:
        db_table = 'Bg_Category_product'

# --- [사용자 행동 테이블] ---

# 3. 리뷰
class Bg_Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE)
    rating = models.FloatField()
    class Meta:
        db_table = 'Bg_Review'

# 4. 장바구니
class Bg_Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE)
    class Meta:
        db_table = 'Bg_Cart'

# 5. 최근 본 상품
class Bg_Recent_product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'Bg_Recent_product'

# 6. 찜 (Wishlist)
class Bg_Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE)
    class Meta:
        db_table = 'Bg_Wishlist'

# 7. 주문 상품
class Bg_Order_Item(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Bg_Product, on_delete=models.CASCADE)
    class Meta:
        db_table = 'Bg_Order_Item'

# 8. 사용자 관심분야 등록
class Bg_User_interest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    interest_category_id = models.IntegerField()
    class Meta:
        db_table = 'Bg_User_interest'

# --- [AI 분석 결과 테이블] ---

# 9. 사용자별 AI 추천 결과
class BgAiRecommendation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        db_column='userid'
    )
    product = models.ForeignKey(
        Bg_Product, 
        on_delete=models.CASCADE, 
        db_column='product_id'
    )
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Bg_Ai_recommendation'
        unique_together = ('user', 'product')


# # 참조 경로(테이블 확정되면)
# class BgAiRecommendation(models.Model):
#     # userid 속성: 장고 관례에 따라 user로 선언하고 db_column을 userid로 지정
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.CASCADE,
#         db_column='userid',  # 실제 DB에 저장될 속성명
#         verbose_name="회원고유번호"
#     )
#     # product_id 속성: 외래키 연결 (다른 앱에 있다면 '앱이름.Bg_Product'로 기재)
#     product = models.ForeignKey(
#         'Bg_Product',
#         on_delete=models.CASCADE,
#         db_column='product_id', # 실제 DB에 저장될 속성명
#         verbose_name="상품번호"
#     )
#     score = models.FloatField(verbose_name="추천점수")
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = 'Bg_Ai_recommendation'
#         unique_together = ('user', 'product') # 중복 추천방지

#     def __str__(self):
#         return f"User:{self.user_id} -> Product:{self.product_id} ({self.score})"