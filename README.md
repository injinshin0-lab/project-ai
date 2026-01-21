현재 실행방법 -> 콘솔 입력

가상환경 설치
python -m venv .venv
실행
.\.venv\Scripts\activate

장고 파이썬에 필요한 모듈 한번에 설치
pip install -r requirements.txt

데이터 생성기 명령(순서대로 권장)

db 있을경우
python manage.py migrate --fake-initial

db 없을경우(그냥 ㄴ)
(!!!!!!!!왠만하면 백엔드에 있을거니까 사용안해도됨!!!!!!!!)
모델 마이그레이션
python manage.py makemigrations
python manage.py migrate


가 데이터 생성
과일상품
python manage.py insert_fruits
과일
python manage.py insert_category_mapping
유저 및 유저행동(주문,찜,장바구니,최근본,리뷰)
python manage.py insert_user_actions

AI알고리즘 실행
python manage.py run_ai
현재 주문, 찜, 장바구니, 최근목록, 리뷰를 바탕으로한 사용자 분석
