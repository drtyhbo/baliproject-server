from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
  url(r'^asset/add/$', 'api.views.add_asset'),
)
