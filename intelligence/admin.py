from django.contrib import admin
from .models import (
    Bg_User,
    Bg_Product, 
    Bg_Interest_category,
    Bg_Category_product_mapping,
    Bg_Order,
    Bg_Order_item, 
    Bg_Wishlist, 
    Bg_Cart, 
    Bg_Recent_product, 
    Bg_Review,
    Bg_AI_recommendation
)

# 모델들을 관리자 페이지에 등록
admin.site.register(Bg_User)
admin.site.register(Bg_Product)
admin.site.register(Bg_Interest_category)
admin.site.register(Bg_Category_product_mapping)
admin.site.register(Bg_Order)
admin.site.register(Bg_Order_item) # 대문자 I에서 소문자 i로 수정
admin.site.register(Bg_Wishlist)
admin.site.register(Bg_Cart)
admin.site.register(Bg_Recent_product)
admin.site.register(Bg_Review)
admin.site.register(Bg_AI_recommendation) # BgAiRecommendation에서 이름 변경