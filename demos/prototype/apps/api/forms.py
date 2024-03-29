from django import forms

class AddAssetForm(forms.Form):
  uid = forms.CharField(max_length=40)
  asset = forms.FileField()
  latitude = forms.FloatField(required=False)
  longitude = forms.FloatField(required=False)
  date_taken = forms.IntegerField()

class GetAssetsForm(forms.Form):
  uid = forms.CharField(max_length=40)
  ts = forms.IntegerField()

class GetPicturesForm(forms.Form):
  uid = forms.CharField(max_length=40)
  ts = forms.IntegerField()

class CreateUserForm(forms.Form):
  uid = forms.CharField(max_length=40)
  name = forms.CharField(max_length=64)
  email = forms.CharField(max_length=128)
