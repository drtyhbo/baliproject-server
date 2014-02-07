import json
import calendar
import datetime
import time

from django.http import HttpResponse
from .forms import AddAssetForm, CreateUserForm
from .models import Asset, User

from django.db.models.query import QuerySet

def encoding_defaults(o):
  if isinstance(o, QuerySet):
    return [obj for obj in o]

  if isinstance(o, set):
    return [obj for obj in o]

  # datetimes to timestamps
  if isinstance(o, datetime):
    return int(time.mktime(o.timetuple()))

  # models that expect to be serialized must define their own to_dict() method
  # OR set an explicit method to use (encode_with), which will take precedence
  if 'encode_with' in dir(o) and callable(getattr(o, 'encode_with')):
    dict_repr = getattr(o, 'encode_with')()
    return dict_repr

  # default to to_dict
  if 'to_dict' in dir(o) and callable(getattr(o,'to_dict')):
    dict_repr = o.to_dict()
    return dict_repr

  raise TypeError

def json_response(data):
  return HttpResponse('%s' % json.dumps(data, default=encoding_defaults),
    mimetype="application/json")

##
#
# Asset API
#
##
def add_asset(request):
  if request.method == 'POST':
    form = AddAssetForm(request.POST, request.FILES)
    if form.is_valid():
      asset = Asset.create(uid=form.cleaned_data['uid'],
          asset_file=request.FILES['asset'],
          latitude=form.cleaned_data['latitude'],
          longitude=form.cleaned_data['longitude'],
          date_taken=datetime.datetime.fromtimestamp(
              form.cleaned_data['date_taken']))
      asset.save()
      # These return values go to the 'moments' app in xcode. To update here
      # you must update there.
      return HttpResponse('success')
  return HttpResponse('error')

def get_asset(request):
  if request.method == 'POST':
    if request.POST.get('uid', None):
      uid = request.POST['uid']
      assets = Asset.objects.filter(uid=uid)

      ret = []
      for asset in assets:
        ret.append({
          'id': asset.id,
          'latitude': asset.latitude,
          'longitude': asset.longitude,
          'dateTaken': calendar.timegm(asset.date_taken.utctimetuple()),
          'url': asset.get_asset_path()
        })
      return json_response(ret)
  return json_response(False)

##
#
# User API
#
##
def add_user(request):
  if request.method == 'POST':
    form = CreateUserForm(request.POST, request.FILES)
    if form.is_valid():
      user = User(uid = form.cleaned_data['uid'],
          name = form.cleaned_data['name'],
          email = form.cleaned_data['email'])
      user.save()
      return json_response(True)
  return json_response(False)

def get_user(request):
  if request.method == 'POST' and request.POST.get('uid', None):
    uid = request.POST.get('uid')
    user = User.objects.get(uid=uid)
    if user:
      return json_response({
        'id': user.id,
        'name': user.name,
        'thumbnailSrc': None
      })
  return json_response(False)
