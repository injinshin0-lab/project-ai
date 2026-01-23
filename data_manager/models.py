from django.db import models

class Bg_Product(models.Model):
    product_name = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    price = models.IntegerField()
    product_status = models.CharField(max_length=20, default='SALE') # 첫번째 코드 길이 20에 맞춤
    origin_name = models.CharField(max_length=255, null=True, blank=True) # 길이 255 확장
    image_url = models.CharField(max_length=500, null=True, blank=True)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False  # 어차피 project.db에 테이블은 있으니까요
        db_table = 'bg_product' # intelligence 모델과 같은 테이블을 바라봄