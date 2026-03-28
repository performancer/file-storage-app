from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.request import Request

from downloads import models
from downloads.serializers import DownloadSerializer
from files.models import File


class DownloadsPerUser(generics.ListAPIView):
    serializer_class = DownloadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_pk = self.kwargs['pk']
        return models.Download.objects.filter(user=user_pk)


class DownloadsPerFile(generics.ListAPIView):
    serializer_class = DownloadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        file_pk = self.kwargs['pk']
        return models.Download.objects.filter(file=file_pk)


class Download(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, pk: int, *args, **kwargs) -> FileResponse:
        file = get_object_or_404(File, pk=pk)

        # record the download
        models.Download.objects.create(file=file, user=request.user, organization=request.user.organization)

        response = FileResponse(file.file)
        response['Content-Disposition'] = f'attachment; filename="{file.file.name.split("/")[-1]}"'
        return response
