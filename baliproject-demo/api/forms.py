from django import forms

class AddAssetForm(forms.Form):
  uid = forms.CharField(max_length=32)
  asset = forms.FileField()
  latitude = forms.FloatField(required=False)
  longitude = forms.FloatField(required=False)
  date_taken = forms.IntegerField()
