from django.urls import path
from .views import (
    AdminLoginView, AdminRefreshView, AdminLogoutView,
    AdminListCreateView, AdminDetailView,
)

urlpatterns = [
    path('login/',                    AdminLoginView.as_view(),       name='admin-login'),
    path('refresh/',                  AdminRefreshView.as_view(),     name='admin-refresh'),
    path('logout/',                   AdminLogoutView.as_view(),      name='admin-logout'),
    path('admins/',                   AdminListCreateView.as_view(),  name='admin-list-create'),
    path('admins/<uuid:admin_id>/',   AdminDetailView.as_view(),      name='admin-detail'),
]
