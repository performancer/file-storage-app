from django.contrib.auth.models import User
from rest_framework import serializers

from files.models import File


class UserSerializer(serializers.ModelSerializer):
    files = serializers.PrimaryKeyRelatedField(
        many=True, queryset=File.objects.all()
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'files']