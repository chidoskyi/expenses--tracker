from django.shortcuts import render
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages

# Create your views here.

def index_preference(request):
    exists = UserPreference.objects.filter(user = request.user).exists()
    user_preferences = None
    
    data = []
    if exists:
        user_preferences = UserPreference.objects.get(user = request.user)
    
        
        file_path = os.path.join(settings.BASE_DIR, 'currencies.json')
        
        # you can still use the 'r' after the file_path 
        with open(file_path) as json_file:
            data = json.load(json_file)
            currency_data = []
            for k,v in data.items():
                currency_data.append({'name': k, 'value': v})
        # to check the json file
        # import pdb
        # pdb.set_trace()
    if request.method == 'GET':
        context = {
            'currency_data': currency_data,
            'user_preferences': user_preferences,
        }
        
        return render(request, 'preference/index2.html', context)
    else:
        currency = request.POST['currency']    
        if exists:
            user_preferences.currency = currency
            user_preferences.save()
        else:
            user_preferences = UserPreference.objects.create(user = request.user, currency=currency)
        messages.success(request, 'Changes Saved')   
        context = {
            'currency_data': currency_data,
            'user_preferences': user_preferences,
        }
        
        return render(request, 'preference/index2.html', context)
