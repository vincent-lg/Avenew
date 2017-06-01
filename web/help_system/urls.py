# URL patterns for the help_system app

from django.conf.urls import url
from web.help_system.views import index

urlpatterns = [
    url(r'^$', index, name="help_index")
]