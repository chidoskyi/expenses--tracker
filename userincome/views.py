from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Source,UserIncome
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.db.models import Q
from django.http import HttpResponse,JsonResponse
from userpreferences.models import UserPreference
from datetime import datetime


@login_required(login_url='/authentication/login')
def index(request):
    sources = Source.objects.all()
    incomes = UserIncome.objects.filter(user = request.user)
    paginator = Paginator(incomes, 3)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        "sources": sources,
        "incomes": incomes,
        "currency": currency,
        "page_obj": page_obj,
    }
    return render(request, 'income/index.html', context )


@login_required()
def add_incomes(request):
    sources = Source.objects.all()
    incomes = UserIncome.objects.filter(user = request.user)
    if request.method == 'POST':
        amount = request.POST.get('amount', None)
        source = request.POST.get('source', None)
        description = request.POST.get('description', None)
        date = request.POST.get('date', None)
    
        if not amount:
            messages.error(request, 'Amount Field Empty')
            return redirect('add-incomes')
        if not description:
            messages.error(request, 'Description Field Empty')
            return redirect('add-incomes')
        try:
            source = Source.objects.get(id=source)
            user_income = UserIncome.objects.create(
                user = request.user,
                amount = amount,
                source=source,
                description=description,
                date = date
            )
            
            user_income.save()
            messages.success(request, 'Record Saved  Successfully')
            return redirect('incomes')
        
        except Source.DoesNotExist:
            messages.error(request, 'Invalid Source')
            return redirect('add-incomes')
        
    context = {
        "sources": sources,
        "incomes": incomes,
        "values": request.POST,
    }
    return render(request, 'income/add-incomes.html', context)

@login_required
def edit_incomes(request, id):
    sources = Source.objects.all()
    incomes = get_object_or_404(UserIncome, pk=id)
    
    if request.method == 'POST':
        amount = request.POST.get('amount', None)
        source_id = request.POST.get('source', None)
        description = request.POST.get('description', None)
        date = request.POST.get('date', None)
    
        if not amount:
            messages.error(request, 'Amount Field Empty')
            return redirect('edit-incomes', id=id)
        
        if not description:
            messages.error(request, 'Description Field Empty')
            return redirect('edit-incomes', id=id)
        
        try:
            source = Source.objects.get(id=source_id)
            incomes.amount = amount
            incomes.source = source
            incomes.description = description
            incomes.date = date
            incomes.save()
            messages.success(request, 'Income Updated Successfully')
            return redirect('incomes')
            
        except Source.DoesNotExist:
            messages.error(request, 'Invalid Source')
            return redirect('edit-incomes', id=id)
        
    context = {
        "sources": sources,
        "incomes": incomes,
        "values": incomes,
    }
    # "values": {
    #         "amount": expenses.amount,
    #         "category": expenses.category.id,  # Assuming category is a ForeignKey
    #         "description": expenses.description,
    #         "date": expenses.date.strftime('%Y-%m-%d') if expenses.date else ''
    #     }
    return render(request, 'income/edit-incomes.html', context)

@login_required
def delete_incomes(request, id):
    incomes = get_object_or_404(UserIncome, pk=id)
    incomes.delete()
    messages.success(request, 'Income deleted successfully.')
    return redirect('incomes')
 

@login_required
def search_incomes(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        search_str = body_data.get('searchText', '')

        # Prefetch related categories to include their names in the response
        incomes = UserIncome.objects.select_related('source').filter(
            Q(amount__istartswith=search_str, user=request.user) |
            Q(date__istartswith=search_str, user=request.user) |
            Q(source__name__icontains=search_str, user=request.user) |
            Q(description__icontains=search_str, user=request.user)
        )

        # Adjust the serializer to include the category name
        data = [
            {
                "id": income.id,
                "amount": income.amount,
                "date": income.date,
                "description": income.description,
                "source": income.source.name  # Access the category name here
            } 
            for income in incomes
        ]

        # Return the modified data as JSON
        return JsonResponse(data, safe=False)
 
 
