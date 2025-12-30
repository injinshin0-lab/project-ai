from django.urls import path
from django.views.decorators.csrf import csrf_exempt # 추가
from . import views

from .views import mock_analysis

urlpatterns = [
    # SpringBoot가 로그 파일을 업로드할 주소: /api/logs/upload/
    path('logs/upload/', views.LogfileUploadView.as_view(), name='log_upload'),

    # 추천 결과를 요청할 주소 (나중에 추가)
    # 예시
    # path('recommend/', views.RecommendView.as_view(), name='recommend'),

    #파이썬 예시
    path('analysis/', csrf_exempt(mock_analysis)),
]