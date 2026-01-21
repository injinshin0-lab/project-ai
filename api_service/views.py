from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
import os

class LogfileUploadView(APIView):
    """
    SpringBoot로부터 로그 파일(예: CSV)을 받아 서버에 저장하고
    추천 모델 학습을 트리거하는 API
    """

    def post(self, request):
        file_obj = request.FILES.get('log_file')

        if not file_obj:
            return Response({"error" : "로그파일을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. 서버의 MEDIA_ROOT 경로에 파일 저장
        # 파일명을 날짜 기반 등으로 변경하면 관리가 편리합니다.
        file_name = file_obj.name
        path = default_storage.save(f'raw_logs/{file_name}', file_obj)
        full_path = default_storage.path(path)

        # 3. (다음 관계에서) 저장된 파일을 읽어 모델 학습/최적화 로직 실행

        return Response({
            "message": "로그 파일 수신 및 저장 완료",
            "file_path": full_path
        }, status=status.HTTP_201_CREATED)


from rest_framework.decorators import api_view
from rest_framework.response import Response

@csrf_exempt
@api_view(['POST'])
def mock_analysis(request):
    # Axios가 보낸 데이터를 일단 출력해서 확인해봅니다.
    print("받은 데이터:", request.data)

    dummy_result = {
        "status" : "success",
        "result" : "데이터 분석 준비 완료 (가짜 데이터)",
        "accuracy": 0.98
    }
    return Response(dummy_result)
