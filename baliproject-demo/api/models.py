from django.db import models

def upload_picture_to(instance, filename):
  return 'profiles/%s/%s' % (
    instance.uid,
    filename)

class Picture(models.Model):
  uid = models.CharField(max_length=32)
  picture = models.ImageField(upload_to=upload_picture_to)
  latitude = models.FloatField(blank=True, null=True)
  longitude = models.FloatField(blank=True, null=True)
  date_taken = models.DateTimeField()
