from rest_framework import generics, permissions

from organizations.models import Organization
from organizations.serializers import OrganizationSerializer


class OrganizationList(generics.ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
