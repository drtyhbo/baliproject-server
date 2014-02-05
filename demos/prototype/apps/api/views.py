import datetime
from django.http import HttpResponse
from .forms import AddAssetForm
from .models import Asset

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
