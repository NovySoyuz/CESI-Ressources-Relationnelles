from django.urls import path
from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "ok", "message": "API RR opérationnelle"})

urlpatterns = [
    path('', health),
    path('api/health/', health),
]