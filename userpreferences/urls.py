from django.urls import path
from .views import index_preference


urlpatterns = [
    path('', index_preference, name='preferences'),
]