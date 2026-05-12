from django.urls import path
from . import views

urlpatterns = [
    path('likes/',     views.LikesListView.as_view(),           name='interaction-likes'),
    path('favoris/',   views.FavorisListView.as_view(),         name='interaction-favoris'),
    path('bookmarks/', views.BookmarksListView.as_view(),       name='interaction-bookmarks'),
    path('exploited/', views.ExploitedListView.as_view(),       name='interaction-exploited'),
    path('summary/',   views.InteractionSummaryView.as_view(),  name='interaction-summary'),
    path('<uuid:resource_id>/', views.InteractionView.as_view(), name='interaction-detail'),
    path('comments/<uuid:resource_id>/', views.CommentListView.as_view(), name='comment-list'),
    path('comments/<uuid:resource_id>/<uuid:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
]
