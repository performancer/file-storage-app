from rest_framework import serializers

from downloads.models import Download


class DownloadSerializer(serializers.ModelSerializer):
    file = serializers.ReadOnlyField(source='file.file.name')
    user = serializers.ReadOnlyField(source='user.username')
    organization = serializers.ReadOnlyField(source='organization.name')

    class Meta:
        model = Download
        fields = ['file', 'downloaded_at', 'user', 'organization']
