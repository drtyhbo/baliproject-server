from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
  url(r'^api/asset/add/$', 'live_mockup.views.add_asset'),
)
