import json
import calendar
import datetime
import time

from django.http import HttpResponse
from .forms import AddAssetForm
from .models import Asset

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
      return HttpResponse('success')
  return HttpResponse('error')

def get_asset(request):
  if request.method == 'GET':
    if request.GET.get('uid', None):
      uid = request.GET['uid']
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
      response = HttpResponse('%s' % json.dumps(ret, default=encoding_defaults),
          mimetype="application/json")
  else:
    response = HttpResponse('error')
  response['Access-Control-Allow-Origin'] = 'null'
  return response
