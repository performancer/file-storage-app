from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from files import views

urlpatterns = [
    path('', views.FileList.as_view()),
    path('<int:pk>', views.FileDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
