from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response

from downloads import models
from downloads.serializers import DownloadSerializer
from files.models import File
from organizations.permissions import IsInOrganization
from users.models import OrganizationUser


class DownloadsPerUser(generics.GenericAPIView):
    serializer_class = DownloadSerializer
    permission_classes = [permissions.IsAuthenticated, IsInOrganization]

    def get_queryset(self) -> QuerySet[models.Download]:
        user_pk = self.kwargs.get('pk')
        user = get_object_or_404(User, pk=user_pk)
        return models.Download.objects.filter(user=user)

    def get(self, request: Request, pk: int, format=None) -> Response:
        downloads = self.get_queryset()
        serializer = self.get_serializer(downloads, many=True)
        return Response(serializer.data)

class DownloadsPerFile(generics.GenericAPIView):
    serializer_class = DownloadSerializer
    permission_classes = [permissions.IsAuthenticated, IsInOrganization]

    def get_queryset(self) -> QuerySet[models.Download]:
        file_pk = self.kwargs.get('pk')
        file = get_object_or_404(File, pk=file_pk)
        return models.Download.objects.filter(file=file)

    def get(self, request: Request, pk: int, format=None) -> Response:
        downloads = self.get_queryset()
        serializer = self.get_serializer(downloads, many=True)
        return Response(serializer.data)

class Download(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsInOrganization]

    def get(self, request: Request, pk: int, *args, **kwargs) -> FileResponse:
        organization = get_object_or_404(OrganizationUser.objects.select_related('organization'), user=request.user).organization
        file = get_object_or_404(File, pk=pk)

        models.Download.objects.create(file=file, user=request.user, organization=organization)

        response = FileResponse(file.file)
        response['Content-Disposition'] = f'attachment; filename="{file.file.name.split("/")[-1]}"'
        return response