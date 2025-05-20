from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from main.models import SettingsForm, Settings
from django.http import HttpResponse, HttpResponseRedirect
import os

# Create your views here.

def main(request):
    return render(request, 'main/main.html')

def success(request):
    return render(request, "main/success.html")

def settings(request):
    settings = Settings.objects.first()
    if request.method == "POST":
        form = SettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/settings/")
    else:
        form = SettingsForm(instance=settings)
    return render(request, 'main/settings.html', {'form': form})

def checkFolder(request):
    path = request.GET['path']
    if path == None:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    if not os.path.exists(path):
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse('Ok')