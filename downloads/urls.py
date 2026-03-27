from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from downloads.views import Download, DownloadsPerUser, DownloadsPerFile

urlpatterns = [
    path('download/<int:pk>', Download.as_view(), name='download'),
    path('downloads/user/<int:pk>', DownloadsPerUser.as_view()),
    path('downloads/file/<int:pk>', DownloadsPerFile.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
