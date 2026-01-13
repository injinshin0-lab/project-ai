현재 실행방법 -> 콘솔 입력


* 장고 파이썬에 필요한 모듈 한번에 설치
  * pip install -r requirements.txt


* AI알고리즘 실행
  * python manage.py run_ai


* 데이터 생성기 명령(순서대로 권장)
* 모델 마이그레이션
  * python manage.py makemigrations data_manager
  * python manage.py migrate data_manager
* 과일상품
  * python manage.py insert_fruits
* 과일
  * python manage.py insert_category_mapping
* 유저 및 유저행동(주문,찜,장바구니,최근본,리뷰)
  * python manage.py insert_user_actions


현재 주문, 찜, 장바구니, 최근목록, 리뷰를 바탕으로한 사용자 분석

개발 할거

1. 분석용 DB 직방으로 연결?
- 2026-01-06 완료
2. 페르소나 데이터 만들기
- 2026-01-06 1차 완료
