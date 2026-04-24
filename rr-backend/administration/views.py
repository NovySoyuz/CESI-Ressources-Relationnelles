# administration/views.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from users.models import User, Citizen
from administration.models import Admin
from administration.serializers import (
    AdminListSerializer,
    AdminDetailSerializer,
    AdminCreateSerializer,
    AdminUpdateSerializer,
)


# ──────────────────────────────────────────────────────────────
# GET  api/administration/admins/
# POST api/administration/admins/
# ──────────────────────────────────────────────────────────────

class AdminListCreateView(APIView):

    def get(self, request):
        admins = Admin.objects.select_related("admin_id__citizen").all()
        serializer = AdminListSerializer(admins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AdminCreateSerializer(data=request.data)
        if serializer.is_valid():
            admin = serializer.save()
            return Response(
                AdminDetailSerializer(admin).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────────────────────
# GET    api/administration/admins/<admin_id>/
# PATCH  api/administration/admins/<admin_id>/
# DELETE api/administration/admins/<admin_id>/
# ──────────────────────────────────────────────────────────────

class AdminDetailView(APIView):

    def get_object(self, admin_id):
        return get_object_or_404(
            Admin.objects.select_related("admin_id__citizen"),
            pk=admin_id,
        )

    def get(self, request, admin_id):
        admin = self.get_object(admin_id)
        serializer = AdminDetailSerializer(admin)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, admin_id):
        admin = self.get_object(admin_id)
        serializer = AdminUpdateSerializer(admin, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                AdminDetailSerializer(admin).data,
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, admin_id):
        admin = self.get_object(admin_id)
        admin.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)