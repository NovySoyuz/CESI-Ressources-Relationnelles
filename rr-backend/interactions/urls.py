from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:resource_id>/', views.InteractionView.as_view(), name='interaction-detail'),
    path('comments/<uuid:resource_id>/', views.CommentListView.as_view(), name='comment-list'),
    path('comments/<uuid:resource_id>/<uuid:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
]
