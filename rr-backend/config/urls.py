from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.urls import include, path
from django.views.decorators.http import require_GET
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

@require_GET
def health(request):
    return JsonResponse({"status": "ok", "message": "API RR opérationnelle"})

urlpatterns = [
    path('', health),
    #path('api/health/', health),
    path('api/auth/', include('users.urls')),
    path('api/resources/', include('resources.urls')),
    path('api/interactions/', include('interactions.urls')),
    #path('api/resources/', include('resources.urls')),
    path('api/administration/', include('administration.urls')),
]
