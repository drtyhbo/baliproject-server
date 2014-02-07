from django.conf.urls import patterns, include, url

urlpatterns = patterns('prototype.apps.api.views',
  url(r'^asset/add/$', 'add_asset'),
  url(r'^asset/get/$', 'get_asset'),
  url(r'^user/add/$', 'add_user'),
  url(r'^user/get/$', 'get_user'),
  url(r'^picture/add/$', 'add_picture'),
  url(r'^picture/get/all/$', 'get_all_pictures'),
)
