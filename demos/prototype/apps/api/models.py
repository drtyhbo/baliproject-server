import json
import os
import urllib2

from django.core.files.storage import default_storage
from django.db import models
from uuid import uuid4
from prototype.utils.location import get_country_name_from_code, get_state_name_from_code

S3_URL = 'https://s3-us-west-1.amazonaws.com/baliproject-demo/%s/%s'

class User(models.Model):
  uid = models.CharField(db_index=True, max_length=40)
  name = models.CharField(max_length=64, blank=True, null=True)
  email = models.CharField(max_length=128, blank=True, null=True)
  thumbnail_url = models.CharField(max_length=256, blank=True, null=True)

class Moment(models.Model):
  user = models.ForeignKey('User')
  earliest_date = models.DateTimeField()
  latest_date = models.DateTimeField()
  location = models.CharField(max_length=256)

  def determine_location(self):
    if self.location:
      return

    pictures = Picture.objects.filter(moment=self).exclude(asset__latitude=0,asset__longitude=0).order_by('asset__date_taken')
    if pictures.count() > 0:
      asset = pictures[0].asset
      geocode_url = 'http://open.mapquestapi.com/geocoding/v1/reverse?key=%s&location=%f,%f' % ('Fmjtd%7Cluur216ynq%2C70%3Do5-90tl1f', asset.latitude, asset.longitude)
      response = urllib2.urlopen(geocode_url)
      if response:
        results = json.loads(response.read())['results']
        location = results[0]['locations'][0]

        city = location['adminArea5']
        state = location['adminArea3']
        country = location['adminArea1']

        if country == 'US':
          self.location = '%s, %s' % (city, get_state_name_from_code(state))
        else:
          self.location = '%s, %s' % (city, get_country_name_from_code(country))

        self.save()

class Asset(models.Model):
  user = models.ForeignKey('User')
  name = models.CharField(max_length=50)
  latitude = models.FloatField(blank=True, null=True)
  longitude = models.FloatField(blank=True, null=True)
  date_taken = models.DateTimeField()
  date_uploaded = models.DateTimeField(auto_now_add=True)

  @staticmethod
  def create(user, asset_file, latitude, longitude, date_taken):
    name = '%s%s' % (uuid4().hex, os.path.splitext(asset_file.name)[1])

    # Upload the file to s3. Do this first so we're not left with orphaned
		# rows in the DB in case it fails.
    file = default_storage.open('%s/%s' % (user.uid, name), 'w')
    for chunk in asset_file.chunks():
      file.write(chunk)
    file.close()

    asset = Asset.objects.create(
      user=user,
      name=name,
      latitude=latitude,
      longitude=longitude,
      date_taken=date_taken,
    )

    return asset

  def get_asset_path(self):
    return S3_URL % (self.user.uid, self.name)

class Picture(models.Model):
  asset = models.ForeignKey('Asset')
  moment = models.ForeignKey('Moment')
  user = models.ForeignKey('User')
  date_uploaded = models.DateTimeField(auto_now_add=True)
  
  
class Share(models.Model):
  shared_by_user = models.ForeignKey('User', related_name='shared_by_user')
  shared_with_users = models.ManyToManyField(User, related_name='shared_with_user')
  shared_assets = models.ManyToManyField(Asset)
  date_shared = models.DateTimeField(auto_now_add=True)
  
  @staticmethod
  def create(shared_by_user_id, shared_with_user_ids, shared_asset_ids):
    
    share = Share.objects.create(
      shared_by_user=shared_by_user_id
    )
    
    #Replace with one query to do multiple inserts
    for user_id in shared_with_user_ids:
      share.shared_with_users.add(user_id)
     
    for shared_asset in shared_assets:
      share.shared_assets.add(shared_asset)
     

    return asset
  
  
    
	
