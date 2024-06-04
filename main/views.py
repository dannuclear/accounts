from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def main(request):
    return render(request, 'main/settingsыыыыы.html')

def settings(request):
    return render(request, 'main/settings.html')