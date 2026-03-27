from django.contrib.auth.models import User
from django.http import Http404, FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, serializers
from rest_framework.response import Response

from downloads import models
from downloads.serializers import DownloadSerializer
from files.models import File
from users.models import OrganizationUser

class DownloadsPerUser(generics.GenericAPIView):
    serializer_class = DownloadSerializer

    def get_queryset(self):
        user_pk = self.kwargs.get('pk')
        user = get_object_or_404(User, pk=user_pk)
        return models.Download.objects.filter(user=user)

    def get(self, request, pk, format=None):
        downloads = self.get_queryset()
        serializer = self.get_serializer(downloads, many=True)
        return Response(serializer.data)

class DownloadsPerFile(generics.GenericAPIView):
    serializer_class = DownloadSerializer

    def get_queryset(self):
        file_pk = self.kwargs.get('pk')
        file = get_object_or_404(File, pk=file_pk)
        return models.Download.objects.filter(file=file)

    def get(self, request, pk, format=None):
        downloads = self.get_queryset()
        serializer = self.get_serializer(downloads, many=True)
        return Response(serializer.data)

class Download(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            organization = OrganizationUser.objects.select_related('organization').get(user=request.user).organization
        except OrganizationUser.DoesNotExist:
            raise serializers.ValidationError('You must belong to an organization to download a file.')

        try:
            file_obj = File.objects.get(pk=pk)
        except File.DoesNotExist:
            raise Http404("File not found.")

        models.Download.objects.create(file=file_obj, user=request.user, organization=organization)

        response = FileResponse(file_obj.file)
        response['Content-Disposition'] = f'attachment; filename="{file_obj.file.name.split("/")[-1]}"'
        return response