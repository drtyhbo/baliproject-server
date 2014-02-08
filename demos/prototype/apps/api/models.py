import os

from django.core.files.storage import default_storage
from django.db import models
from uuid import uuid4

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

class Asset(models.Model):
  user = models.ForeignKey('User')
  name = models.CharField(max_length=50)
  latitude = models.FloatField(blank=True, null=True)
  longitude = models.FloatField(blank=True, null=True)
  date_taken = models.DateTimeField()

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
