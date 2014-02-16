import json
import calendar
import datetime
import forms
<<<<<<< HEAD
from itertools import chain
=======
import logging
import time
>>>>>>> 28202528b54e18157a193149b52decd10c59272f

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from .models import Asset, Moment, Picture, User, Share

from django.db.models.query import QuerySet
    

def encoding_defaults(o):
  if isinstance(o, QuerySet):
    return [obj for obj in o]

  if isinstance(o, set):
    return [obj for obj in o]

  # datetimes to timestamps
  if isinstance(o, datetime.datetime):
    return calendar.timegm(o.utctimetuple())

  # models that expect to be serialized must define their own to_dict() method
  # OR set an explicit method to use (encode_with), which will take precedence
  if 'encode_with' in dir(o) and callable(getattr(o, 'encode_with')):
    dict_repr = getattr(o, 'encode_with')()
    return dict_repr

  # default to to_dict
  if 'to_dict' in dir(o) and callable(getattr(o, 'to_dict')):
    dict_repr = o.to_dict()
    return dict_repr

  raise TypeError

def json_response(data):
  return HttpResponse('%s' % json.dumps(data, default=encoding_defaults),
    mimetype="application/json")

# #
#
# Asset API
#
# #
def add_asset(request):
  if request.method == 'POST':
    form = forms.AddAssetForm(request.POST, request.FILES)
    if form.is_valid():
      uid = form.cleaned_data['uid']
      # This might be called before a user object has been created.
      try:
        user = User.objects.get(uid=uid)
      except ObjectDoesNotExist:
        user = User.objects.create(uid=uid)

      asset = Asset.create(user=user,
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
    form = forms.GetAssetsForm(request.POST)
    if form.is_valid():
      uid = form.cleaned_data['uid']
      ts = datetime.datetime.utcfromtimestamp(form.cleaned_data['ts'])

      # Only grab assets that were uploaded after the provided timestamp to
      # speed things up.
      assets = Asset.objects.filter(user__uid=uid, date_uploaded__gt=ts).order_by('-date_uploaded')

      # Always return the timestamp and list of assets to simplify the
      # frontend code.
      ret = {
        'ts': ts,
        'assets': []
      }
      if assets.count() > 0:
        ret['ts'] = assets[0].date_uploaded
        for asset in assets:
          ret['assets'].append({
            'id': asset.id,
            'latitude': asset.latitude,
            'longitude': asset.longitude,
            'dateTaken': asset.date_taken,
            'url': asset.get_asset_path(),
            'dateUploaded': asset.date_uploaded
          })
      return json_response(ret)
  return json_response(False)

# #
#
# User API
#
# #
def add_user(request):
  if request.method == 'POST':
    form = forms.CreateUserForm(request.POST)
    if form.is_valid():
      # The user object may already exist with only the uid field filled
      # in.
      try:
        user = User.objects.get(uid=form.cleaned_data['uid'])
      except ObjectDoesNotExist:
        user = User(uid=form.cleaned_data['uid'])

      user.name = form.cleaned_data['name']
      user.email = form.cleaned_data['email']
      user.save()

      return json_response({
        'id': user.id,
        'name': user.name,
        'thumbnailSrc': None
      })
  return json_response(False)

def get_user(request):
  if request.method == 'POST' and request.POST.get('uid', None):
    uid = request.POST.get('uid')
    try:
      user = User.objects.get(uid=uid)
    except ObjectDoesNotExist:
      user = None

    if user:
      return json_response({
        'id': user.id,
        'name': user.name,
        'thumbnailSrc': None
      })
  return json_response(False)

# #
#
# Picture API
#
# #

# Returns true if the two assets should be clustered together.
def are_assets_clustered(asset1, asset2):
  return (asset2.date_taken - asset1.date_taken).total_seconds() < 2 * 60 * 60

# Returns a list of lists where each sublist is a set of pictures that are
# related to eachother. Each of these sublists forms the basis for a moment.
# The moment field of each Picture object has NOT been populated.
def get_clustered_pictures_from_assets(assets):
  clustered_pictures = []
  current_cluster = []
  prev_asset = None

  for asset in assets:
    picture = Picture(asset=asset,
        user=asset.user)
    if prev_asset and not are_assets_clustered(prev_asset, asset):
      clustered_pictures.append(current_cluster)
      current_cluster = []
    current_cluster.append(picture)
    prev_asset = asset

  clustered_pictures.append(current_cluster)

  return clustered_pictures

# Given a cluster of pictures, returns the moment object that will contain
# that cluster.
def get_moment_for_cluster(cluster):
  time_delta = datetime.timedelta(hours=2)
  earliest_date = cluster[0].asset.date_taken - time_delta
  latest_date = cluster[-1].asset.date_taken + time_delta

  # Grab all the moments that fall between the earliest date and the latest
  # date.
  moments = Moment.objects.filter(
      Q(earliest_date__lte=earliest_date) & Q(latest_date__gte=earliest_date) | 
      Q(earliest_date__lte=latest_date) & Q(latest_date__gte=latest_date) | 
      Q(earliest_date__gte=earliest_date) & Q(latest_date__lte=latest_date) | 
      Q(earliest_date__lte=earliest_date) & Q(latest_date__gte=latest_date)).order_by('latest_date')

  moment = None

  # Create a new moment.
  if len(moments) == 0:
    moment = Moment.objects.create(user=cluster[0].user,
        earliest_date=earliest_date,
        latest_date=latest_date)
  # Only one moment, update this dude.
  elif len(moments) == 1:
    moment = moments[0]
    if earliest_date < moment.earliest_date:
      moment.earliest_date = earliest_date
    if latest_date > moment.latest_date:
      moment.latest_date = latest_date
  # Multiple moments, create a new moment, and delete the old ones.
  else:
    moment = Moment.objects.create(user=cluster[0].user,
        earliest_date=moments[0].earliest_date < earliest_date and \
            moments[0].earliest_date or earliest_date,
        latest_date=moments[len(moments) - 1].latest_date > latest_date and \
            moments[len(moments) - 1].latest_date or latest_date)
    Picture.objects.filter(moment__in=moments).update(moment=moment)

  return moment 

# Given a list of asset_ids, returns a list of picture objects that have been
# saved to the database.
def create_pictures_from_asset_ids(asset_ids):
  assets = Asset.objects.filter(pk__in=asset_ids).order_by('date_taken')
  clustered_pictures = get_clustered_pictures_from_assets(assets)

  pictures = []
  for cluster in clustered_pictures:
    moment = get_moment_for_cluster(cluster)
    for picture in cluster:
      picture.moment = moment
      picture.save()
      pictures.append(picture)
    moment.determine_location()
  return pictures

def add_picture(request):
  if request.method == 'POST' and request.POST.get('uid', None) and \
      request.POST.getlist('id[]', None):
    uid = request.POST.get('uid')
    asset_ids = request.POST.getlist('id[]')

    # This might be called before a user object has been created.
    try:
      user = User.objects.get(uid=uid)
    except ObjectDoesNotExist:
      user = User.objects.create(uid=uid)
      
    if user == None:
      return json_response(False)

    pictures = create_pictures_from_asset_ids(asset_ids)

    ret = []
    for picture in pictures:
      asset = picture.asset
      ret.append({
        'id': picture.id,
        'assetId': asset.id,
        'pictureSrc': asset.get_asset_path(),
        'thumbnailPictureSrc': asset.get_asset_path()
      })
    return json_response(ret)

  return json_response(False)

def get_all_pictures(request):
  if request.method == 'POST':
    form = forms.GetPicturesForm(request.POST)
    if form.is_valid():
      uid = form.cleaned_data['uid']
      ts = datetime.datetime.utcfromtimestamp(form.cleaned_data['ts'])
    
      try:
        user = User.objects.get(uid=uid)
      except ObjectDoesNotExist:
        user = None

      if user:
        ret = {
          'ts': ts,
          'pictures': []
        }

        pictures = Picture.objects.filter(user=user, date_uploaded__gt=ts).order_by('-date_uploaded')
        if pictures.count() > 0:
          ret['ts'] = pictures[0].date_uploaded
          for picture in pictures:
            ret['pictures'].append({
              'id': picture.id,
              'assetId': picture.asset.id,
              'url': picture.asset.get_asset_path()
            })
        return json_response(ret)

  return json_response(False)

# #
#
# Moments API
#
# #
def get_all_moments(request):
    if request.method == 'POST' and request.POST.get('uid', None):
        uid = request.POST.get('uid')
    
        try:
            user = User.objects.get(uid=uid)
        except ObjectDoesNotExist:
            user = None

        if user:
            ret = []

            moments = Moment.objects.filter(user=user).order_by('-earliest_date')
            for moment in moments:
                ret_moment = {
                    'id': moment.id,
                    'timestamp': moment.earliest_date,
                    'location': moment.location,
                    'pictures': []
                }
                pictures = Picture.objects.filter(moment=moment).order_by('asset__date_taken')
                for picture in pictures:
                    ret_moment['pictures'].append({
                        'id': picture.id,
                        'assetId': picture.asset.id,
                        'pictureSrc': picture.asset.get_asset_path(),
                        'timestamp': picture.asset.date_taken,
                        'thumbnailPictureSrc': picture.asset.get_asset_path()
                    })
                ret.append(ret_moment)
            return json_response(ret)
    return json_response(False)

# #
#
# Share API
#
# #    
def add_share(request):
  if request.method == 'POST' and \
      request.POST.getlist('sharedWith[]', None) and \
      request.POST.getlist('sharedAssets[]', None):
    
    sharedBy = request.POST.get('sharedBy')
    try:
      user = User.objects.get(uid=sharedBy)
    except ObjectDoesNotExist:
      user = None

    if user == None:
      return json_response(False)
    
    shared_with_user_ids = request.POST.getlist('sharedWith[]')
    shared_asset_ids = request.POST.getlist('sharedAssets[]')

    share = Share.create(user.id, shared_with_user_ids, shared_asset_ids)
    share.save();

    return json_response({
      'id': share.id
      })
  return json_response(False)

def get_all_shares(request):
    if request.method == 'POST' and request.POST.get('uid', None):
        uid = request.POST.get('uid')
    
        try:
            user = User.objects.get(uid=uid)
        except ObjectDoesNotExist:
            user = None
            
        if user == None:
          return json_response(False)

        
        user_shares = Share.objects.filter(Q(shared_by_user_id=user.id)) 
        others_shares =  Share.objects.filter(Q(shared_with_users__id = user.id)) 

        shares = sorted(chain(user_shares, others_shares), 
               key= lambda instance: instance.date_shared)
        
        
        ret = []
        for share in shares:
            ret_share = {
                'id': share.id,
                'dateShared': share.date_shared,
                'sharedBy': share.shared_by_user_id,
                'sharedAssets': [],
                'sharedWith': []
            }
            assets = share.shared_assets.all()
            for asset in assets:
                ret_share['sharedAssets'].append({
                  'id': asset.id,
                  'url': asset.get_asset_path()
                })
            users = share.shared_with_users.all()
            for user in users:
                ret_share['sharedWith'].append({
                  'id': user.id,
                  'url': user.thumbnail_url,
                })
            ret.append(ret_share)
        return json_response(ret)
    return json_response(False)
 
    
    

    
    
    
