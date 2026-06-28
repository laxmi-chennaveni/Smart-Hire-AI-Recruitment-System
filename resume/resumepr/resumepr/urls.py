from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Smart Hire AI is Live! 🚀</h1>")

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
]
