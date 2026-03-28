from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser

from files.models import File
from files.serializers import FileSerializer


class FileList(generics.ListCreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer: FileSerializer):
        serializer.save(owner=self.request.user, organization=self.request.user.organization)


class FileDetail(generics.RetrieveAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
