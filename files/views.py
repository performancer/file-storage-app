from rest_framework import generics

from files.models import File
from files.serializers import FileSerializer


class FileList(generics.ListCreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer

class FileDetail(generics.RetrieveAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
