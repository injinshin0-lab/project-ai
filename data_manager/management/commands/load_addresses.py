import sqlite3
import random
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'SQLite 직접 쿼리를 통해 유저당 1개씩 배송지 데이터를 생성합니다.'

    def handle(self, *args, **options):
        # 1. DB 연결 설정
        db_path = str(settings.DATABASES['default']['NAME'])
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        self.stdout.write("--- 배송지(Bg_Address) 데이터 생성 시작 ---")

        # 2. 초기화 (기존 데이터 삭제 및 시퀀스 리셋)
        try:
            cursor.execute("DELETE FROM Bg_Address")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='Bg_Address'")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"초기화 중 알림: {e}"))

        # 3. 데이터 생성을 위한 기초 리소스
        cities = ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시", "세종특별자치시"]
        provinces = [
            "경기도 수원시", "경기도 용인시", "경기도 고양시", "강원도 춘천시", "강원도 원주시",
            "충청북도 청주시", "충청남도 천안시", "전라북도 전주시", "전라남도 목포시",
            "경상북도 포항시", "경상북도 구미시", "경상남도 창원시", "경상남도 김해시", "제주특별자치도 제주시"
        ]
        all_regions = cities + provinces

        # 4. 기존 유저 ID 목록 가져오기
        cursor.execute("SELECT id FROM Bg_User")
        user_ids = [row[0] for row in cursor.fetchall()]

        if not user_ids:
            self.stdout.write(self.style.ERROR("유저 데이터가 없습니다. 유저 생성을 먼저 진행해주세요."))
            conn.close()
            return

        # 5. 주소 데이터 빌드
        address_list = []
        for i, u_id in enumerate(user_ids, 1):
            recipient = f"수령인 test {i}"
            base_addr = random.choice(all_regions)
            road_num = f"{random.randint(1, 100)}-{random.randint(1, 50)}"
            address = f"{base_addr} {road_num}"
            detail = f"{random.randint(101, 999)}동 {random.randint(101, 2505)}호"
            postcode = f"{random.randint(10000, 99999):05d}"
            phone = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            is_default = 1
            
            # (user_id, recipient, postcode, address, detail_address, is_default, recipient_phone)
            address_list.append((u_id, recipient, postcode, address, detail, is_default, phone))

        # 6. SQL 실행 (executemany로 한꺼번에 삽입)
        cursor.executemany("""
            INSERT INTO Bg_Address (user_id, recipient, postcode, address, detail_address, is_default, recipient_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, address_list)

        # 7. 저장 및 종료
        conn.commit()
        conn.close()
        self.stdout.write(self.style.SUCCESS(f"성공: {len(address_list)}명의 유저에게 배송지 할당이 완료되었습니다."))