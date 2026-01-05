# intelligence/management/commands/run_ai.py
from django.core.management.base import BaseCommand
from intelligence.services.ai_analyzer import AiRecommender
import time

class Command(BaseCommand):
    help = '스키마 기반 AI 추천 엔진을 실행합니다.'

    def handle(self, *args, **options):
        start_time = time.time()
        self.stdout.write(self.style.SUCCESS("--- 추천 엔진 프로세스 시작 ---"))
        
        try:
            recommender = AiRecommender()
            
            # 1. 외부 DB(Bg_User, Bg_Product 등)에서 데이터 동기화
            self.stdout.write("1. 데이터 동기화 중 (External DB -> Django DB)...")
            recommender.sync_from_external()
            
            # 2. 동기화된 데이터를 바탕으로 점수화(Processing)
            self.stdout.write("2. 행동 데이터 수집 및 가중치 계산 중...")
            recommender.collect_data()
            
            # 3. 하이브리드 협업 필터링 분석 실행
            self.stdout.write("3. 하이브리드 추천 엔진 분석 가동...")
            recommender.run_analysis()
            
            # 4. 분석 결과 저장 (내부 DB 및 외부 Bg_AI_recommendation 테이블)
            self.stdout.write("4. 분석 결과 적재 및 동기화 중...")
            recommender.save_results_to_db()
            
            end_time = time.time()
            elapsed_time = round(end_time - start_time, 2)
            self.stdout.write(self.style.SUCCESS(f"--- 모든 공정 완료 ({elapsed_time}초 소요) ---"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"!!! 엔진 실행 중 치명적 오류 발생: {e}"))