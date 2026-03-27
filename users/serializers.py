from django.contrib.auth.models import User
from rest_framework import serializers

from files.serializers import FileSerializer
from organizations.serializers import OrganizationSerializer
from users.models import OrganizationUser


class UserSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    files = FileSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'organization', 'files']

    def get_organization(self, obj: User):
        try:
            org_user = OrganizationUser.objects.get(user=obj)
            return OrganizationSerializer(org_user.organization).data
        except OrganizationUser.DoesNotExist:
            return None
