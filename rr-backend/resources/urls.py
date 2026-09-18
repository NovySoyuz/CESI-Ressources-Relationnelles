from django.urls import path
from . import views

urlpatterns = [
    path('', views.ResourceListCreateView.as_view(), name='resource-list'),
    path('categories/', views.CategoryListView.as_view(), name='resource-categories'),
    path('relations/', views.RelationListView.as_view(), name='resource-relations'),
    path('pending/', views.ResourcePendingView.as_view(), name='resource-pending'),
    path('<uuid:resource_id>/', views.ResourceDetailView.as_view(), name='resource-detail'),
    path('<uuid:resource_id>/publish/', views.ResourcePublishView.as_view(), name='resource-publish'),
]
