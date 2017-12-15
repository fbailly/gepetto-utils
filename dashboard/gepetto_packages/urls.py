from django.conf.urls import url
from django.contrib import admin
from django.views.generic import ListView

from .models import Package

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', ListView.as_view(model=Package)),
]