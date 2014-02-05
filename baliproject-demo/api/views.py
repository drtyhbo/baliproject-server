import datetime
from django.http import HttpResponse
from .forms import AddAssetForm
from .models import Picture

def add_asset(request):
  if request.method == 'POST':
    form = AddAssetForm(request.POST, request.FILES)
    if form.is_valid():
      picture = Picture(uid=form.cleaned_data['uid'],
          picture=request.FILES['picture'],
          date_taken=datetime.datetime.fromtimestamp(
              form.cleaned_data['date_taken']))
      picture.save()
      return HttpResponse('a-ok')
  else:
    form = AddAssetForm()
  return HttpResponse('<form method="POST" action="." enctype="multipart/form-data">%s<input type="submit" value="submit"></form>' % form)
