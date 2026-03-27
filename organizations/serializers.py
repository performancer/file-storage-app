from rest_framework import serializers

from organizations.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    download_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ['id', 'name', 'created', 'download_count']

    def get_download_count(self, obj: Organization):
        return obj.downloads.count()