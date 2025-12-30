from django.core.management.base import BaseCommand
from intelligence.services.recommender import AiRecommender

class Command(BaseCommand):
    help = 'Run AI Collaborative Filtering for Products'

    def handle(self, *args, **options):
        engine = AiRecommender()
        self.stdout.write("Collecting user behavior data...")
        engine.collect_data()
        self.stdout.write("Analyzing similarities...")
        engine.run_analysis()
        self.stdout.write("Storing results to Bg_Ai_recommendation...")
        engine.save_results_to_db()
        self.stdout.write(self.style.SUCCESS("AI Recommendation successfully updated!"))


