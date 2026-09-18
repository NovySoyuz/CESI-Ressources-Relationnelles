from django.urls import path
from .views import (
    AdminLoginView, AdminRefreshView, AdminLogoutView,
    AdminListCreateView, AdminDetailView,
    AdminResourceListView, AdminResourcePendingView,
    AdminResourcePublishView, AdminResourceDeleteView,
    AdminUserListView,
)

urlpatterns = [
    path('login/',                                      AdminLoginView.as_view(),           name='admin-login'),
    path('refresh/',                                    AdminRefreshView.as_view(),          name='admin-refresh'),
    path('logout/',                                     AdminLogoutView.as_view(),           name='admin-logout'),
    path('admins/',                                     AdminListCreateView.as_view(),       name='admin-list-create'),
    path('admins/<uuid:admin_id>/',                     AdminDetailView.as_view(),           name='admin-detail'),
    path('resources/',                                  AdminResourceListView.as_view(),     name='admin-resource-list'),
    path('resources/pending/',                          AdminResourcePendingView.as_view(),  name='admin-resource-pending'),
    path('resources/<uuid:resource_id>/publish/',       AdminResourcePublishView.as_view(),  name='admin-resource-publish'),
    path('resources/<uuid:resource_id>/',               AdminResourceDeleteView.as_view(),   name='admin-resource-delete'),
    path('users/',                                      AdminUserListView.as_view(),          name='admin-user-list'),
]
