# intelligence/management/commands/run_ai.py
from django.core.management.base import BaseCommand
from intelligence.services.ai_analyzer import AiRecommender # 경로 확인 필수
import time

class Command(BaseCommand):
    help = 'project.db 직접 분석 기반 AI 추천 엔진을 실행합니다.'

    def handle(self, *args, **options):
        start_time = time.time()
        self.stdout.write(self.style.SUCCESS("--- 추천 엔진 프로세스 시작 ---"))
        
        try:
            recommender = AiRecommender()
            
            # 장고가 직접 project.db를 읽기 때문입니다.
            
            # 1. 행동 데이터 수집 및 가중치 계산
            self.stdout.write("1. 실시간 행동 데이터 수집 중...")
            if not recommender.collect_data():
                self.stdout.write(self.style.WARNING("분석할 행동 데이터가 부족하여 중단합니다."))
                return
            
            # 2. 하이브리드 협업 필터링 분석 실행
            self.stdout.write("2. 하이브리드 추천 엔진 분석 가동 (CF + 카테고리 보너스)...")
            recommender.run_analysis()
            
            # 3. 분석 결과 저장 (Bg_AI_recommendation 테이블에 직접 적재)
            self.stdout.write("3. 최종 분석 결과 project.db 적재 중...")
            recommender.save_results_to_db()
            
            end_time = time.time()
            elapsed_time = round(end_time - start_time, 2)
            self.stdout.write(self.style.SUCCESS(f"--- 모든 공정 완료 ({elapsed_time}초 소요) ---"))

        except Exception as e:
            # 에러 발생 시 상세 정보 출력
            self.stdout.write(self.style.ERROR(f"!!! 엔진 실행 중 치명적 오류 발생: {e}"))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))