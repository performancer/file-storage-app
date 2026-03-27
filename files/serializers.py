from rest_framework import serializers

from files.models import File
from users.models import OrganizationUser


class FileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    organization = serializers.ReadOnlyField(source='organization.name')

    class Meta:
        model = File
        fields = ['id', 'file', 'created', 'owner', 'organization']

    def validate(self, attrs):
        user = self.context['request'].user

        try:
            org_user = OrganizationUser.objects.get(user=user)
        except OrganizationUser.DoesNotExist:
            raise serializers.ValidationError('You must belong to an organization to upload a file.')

        attrs['organization'] = org_user.organization
        return attrs
