from rest_framework import serializers

from files.models import File


class FileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = File
        fields = ['id', 'name', 'created', 'owner']
