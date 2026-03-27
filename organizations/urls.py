from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from organizations.views import OrganizationList

urlpatterns = [
    path('', OrganizationList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
