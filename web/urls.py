"""
Url definition file to redistribute incoming URL requests to django
views. Search the Django documentation for "URL dispatcher" for more
help.

"""
from django.conf.urls import url, include
# default evennia patterns
from evennia.web.urls import urlpatterns

# eventual custom patterns
custom_patterns = [
    url(r'^builder/', include('web.builder.urls',
            namespace='builder', app_name='builder')),
    url(r'^help/', include('web.help_system.urls',
            namespace='help_system', app_name='help_system')),
    url(r'^wiki/', include('evennia_wiki.urls',
            namespace='wiki', app_name='wiki')),
    url(r'^amwhook/', include('anymail.urls')),
]

# this is required by Django.
urlpatterns = custom_patterns + urlpatterns
