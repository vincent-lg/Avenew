# URL patterns for the builder app

from django.conf.urls import url
from web.builder import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^batch$', views.batch, name="batch")
]