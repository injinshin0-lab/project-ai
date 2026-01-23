from django.core.management import call_command
from rest_framework.response import Response

# 접근권한 막히는것을 방지하기 위한 접근허용
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny

# ai 실행커맨드를 post로 보낼
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny]) # 권한 체크 제외
def trigger_ai_run(request):
    try:
        # intelligence 폴더 안의 run_ai 커맨드를 실행
        call_command('run_ai')
        return Response({"status": "success", "message": "AI 추천 엔진 가동 완료!"})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)