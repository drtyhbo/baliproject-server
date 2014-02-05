import os

from django.core.files.storage import default_storage
from django.db import models
from uuid import uuid4

class Asset(models.Model):
  uid = models.CharField(max_length=40)
  name = models.CharField(max_length=50)
  latitude = models.FloatField(blank=True, null=True)
  longitude = models.FloatField(blank=True, null=True)
  date_taken = models.DateTimeField()

  @staticmethod
  def create(uid, asset_file, latitude, longitude, date_taken):
    name = '%s%s' % (uuid4().hex, os.path.splitext(asset_file.name)[1])
    asset = Asset.objects.create(
      uid=uid,
      name=name,
      latitude=latitude,
      longitude=longitude,
      date_taken=date_taken,
    )

    # Upload the file to s3.
    file = default_storage.open('%s/%s' % (uid, name), 'w')
    for chunk in asset_file.chunks():
      file.write(chunk)
    file.close()

    return asset
