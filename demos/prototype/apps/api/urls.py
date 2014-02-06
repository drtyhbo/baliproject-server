from django.conf.urls import patterns, include, url

urlpatterns = patterns('prototype.apps.api.views',
  url(r'^asset/add/$', 'add_asset'),
  url(r'^asset/get/$', 'get_asset'),
)
