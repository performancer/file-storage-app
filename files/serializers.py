import os

from rest_framework import serializers
from rest_framework.reverse import reverse

from files.models import File
from users.models import OrganizationUser


class FileSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()
    owner = serializers.ReadOnlyField(source='owner.username')
    organization = serializers.ReadOnlyField(source='organization.name')
    download_url = serializers.SerializerMethodField()
    download_count = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = ['id', 'file', 'file_name', 'download_url', 'download_count', 'created', 'owner', 'organization']

    def get_file_name(self, obj):
        return os.path.basename(obj.file.name)

    def get_download_url(self, obj):
        request = self.context.get('request')
        url = reverse('download', args=[obj.pk])
        return request.build_absolute_uri(url) if request else url

    def get_download_count(self, obj):
        return obj.downloads.count()

    def validate(self, attrs):
        user = self.context['request'].user

        try:
            org_user = OrganizationUser.objects.get(user=user)
        except OrganizationUser.DoesNotExist:
            raise serializers.ValidationError('You must belong to an organization to upload a file.')

        attrs['organization'] = org_user.organization
        return attrs
