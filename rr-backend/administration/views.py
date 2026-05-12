from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import AccessToken

from .models import Admin
from .serializers import (
    AdminLoginSerializer,
    AdminListSerializer,
    AdminDetailSerializer,
    AdminCreateSerializer,
    AdminUpdateSerializer,
)


# ── Auth ──────────────────────────────────────────────────────────────────────

class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(
            data=request.data,
            context={'request': request},
        )

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(
                {'detail': 'Identifiants incorrects ou compte non administrateur.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class AdminRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code != status.HTTP_200_OK:
            return response

        try:
            new_access  = response.data.get('access')
            new_refresh = response.data.get('refresh')

            decoded = AccessToken(new_access)
            user_id = decoded.get('user_id')

            Admin.objects.filter(admin_id=user_id).update(
                admin_token=new_access,
                admin_refresh_token=new_refresh,
            )
        except Exception:
            pass

        return response


class AdminLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.admin_profile.invalidate_tokens()
        except Admin.DoesNotExist:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)


# ── CRUD ──────────────────────────────────────────────────────────────────────

class AdminListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        admins = Admin.objects.select_related('admin_id').all()
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


class AdminDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, admin_id):
        return get_object_or_404(Admin.objects.select_related('admin_id'), pk=admin_id)

    def get(self, request, admin_id):
        serializer = AdminDetailSerializer(self.get_object(admin_id))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, admin_id):
        admin = self.get_object(admin_id)
        serializer = AdminUpdateSerializer(admin, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(AdminDetailSerializer(admin).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, admin_id):
        self.get_object(admin_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
