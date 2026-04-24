# administration/urls.py

from django.urls import path
from administration.views import AdminListCreateView, AdminDetailView

urlpatterns = [
    path("admins/",          AdminListCreateView.as_view(), name="admin-list-create"),
    path("admins/<uuid:admin_id>/", AdminDetailView.as_view(),        name="admin-detail"),
]