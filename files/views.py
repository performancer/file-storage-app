from rest_framework import generics, permissions
from rest_framework.parsers import FormParser, MultiPartParser

from files.models import File
from files.serializers import FileSerializer
from organizations.permissions import IsInOrganization


class FileList(generics.ListCreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated, IsInOrganization]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class FileDetail(generics.RetrieveAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated, IsInOrganization]
