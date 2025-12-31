# intelligence/management/commands/run_ai.py
from django.core.management.base import BaseCommand
from intelligence.services.recommender import AiRecommender

class Command(BaseCommand):
    help = 'AI 추천 엔진을 실행합니다.'

    def handle(self, *args, **options):
        self.stdout.write("--- 추천 엔진 시작 ---")
        
        recommender = AiRecommender()
        recommender.sync_from_external()
        recommender.collect_data()
        recommender.run_analysis()
        recommender.save_results_to_db()
        
        self.stdout.write(self.style.SUCCESS("--- 모든 공정 완료 ---"))