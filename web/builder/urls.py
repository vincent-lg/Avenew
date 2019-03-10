# URL patterns for the builder app

from django.conf.urls import url
from web.builder import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^batch$', views.batch_list, name="batches"),
    url(r'^batch/(.+)$', views.batch_view, name="batch"),
    url(r'^batch/apply$', views.batch_apply, name="batch_apply"),
]
