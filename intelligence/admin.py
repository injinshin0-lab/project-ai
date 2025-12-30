from django.contrib import admin
from .models import (
    Bg_Product, 
    Bg_Order_Item, 
    Bg_Wishlist, 
    Bg_Cart, 
    Bg_Recent_product, 
    Bg_Review,
    BgAiRecommendation
)

# Register your models here.
admin.site.register(Bg_Product)
admin.site.register(Bg_Wishlist)
admin.site.register(Bg_Order_Item)
admin.site.register(Bg_Cart)
admin.site.register(Bg_Recent_product)
admin.site.register(Bg_Review)
admin.site.register(BgAiRecommendation)