from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Category,Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from userpreferences.models import UserPreference
import datetime
import csv
import xlwt 
from django.template.loader import render_to_string
import tempfile
from django.db.models import Sum
import cairosvg

# Create your views here.

@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(user = request.user)
    paginator = Paginator(expenses, 3)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    try:
        user_preference = UserPreference.objects.get(user=request.user)
        currency = user_preference.currency
    except UserPreference.DoesNotExist:
        # Handle the case where the user preference does not exist
        currency = 'USD'  # or any default value you want to use
        # Optionally, you can create a default UserPreference for the user
        UserPreference.objects.create(user=request.user, currency=currency)
    context = {
        "categories": categories,
        "expenses": expenses,
        "currency": currency,
        "page_obj": page_obj,
    }
    return render(request, 'expenses/index.html', context )

@login_required
def add_expenses(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(user = request.user)
    if request.method == 'POST':
        amount = request.POST.get('amount', None)
        category = request.POST.get('category', None)
        description = request.POST.get('description', None)
        date = request.POST.get('date', None)
    
        if not amount:
            messages.error(request, 'Amount Field Empty')
            return redirect('add-expenses')
        if not description:
            messages.error(request, 'Description Field Empty')
            return redirect('add-expenses')
        try:
            category = Category.objects.get(id=category)
            user_expense = Expense.objects.create(
                user = request.user,
                amount = amount,
                category=category,
                description=description,
                date = date
            )
            
            user_expense.save()
            messages.success(request, 'Expenses Added Successfully')
            return redirect('expenses')
        
        except Category.DoesNotExist:
            messages.error(request, 'Invalid Category')
            return redirect('add-expenses')
        
    context = {
        "categories": categories,
        "expenses": expenses,
        "values": request.POST,
    }
    return render(request, 'expenses/add-expenses.html', context)

@login_required
def edit_expenses(request, id):
    categories = Category.objects.all()
    expenses = get_object_or_404(Expense, pk=id)
    
    if request.method == 'POST':
        amount = request.POST.get('amount', None)
        category_id = request.POST.get('category', None)
        description = request.POST.get('description', None)
        date = request.POST.get('date', None)
    
        if not amount:
            messages.error(request, 'Amount Field Empty')
            return redirect('edit-expenses', id=id)
        
        if not description:
            messages.error(request, 'Description Field Empty')
            return redirect('edit-expenses', id=id)
        
        try:
            category = Category.objects.get(id=category_id)
            expenses.amount = amount
            expenses.category = category
            expenses.description = description
            expenses.date = date
            expenses.save()
            messages.success(request, 'Expense Updated Successfully')
            return redirect('expenses')
            
        except Category.DoesNotExist:
            messages.error(request, 'Invalid Category')
            return redirect('edit-expenses', id=id)
        
    context = {
        "categories": categories,
        "expenses": expenses,
        "values": expenses,
    }
    # "values": {
    #         "amount": expenses.amount,
    #         "category": expenses.category.id,  # Assuming category is a ForeignKey
    #         "description": expenses.description,
    #         "date": expenses.date.strftime('%Y-%m-%d') if expenses.date else ''
    #     }
    return render(request, 'expenses/edit-expenses.html', context)

@login_required
def delete_expenses(request, id):
    expense = get_object_or_404(Expense, pk=id)
    expense.delete()
    messages.success(request, 'Expense deleted successfully.')
    return redirect('expenses')
 

@login_required
def search_expenses(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        search_str = body_data.get('searchText', '')

        # Prefetch related categories to include their names in the response
        expenses = Expense.objects.select_related('category').filter(
            Q(amount__istartswith=search_str, user=request.user) |
            Q(date__istartswith=search_str, user=request.user) |
            Q(category__name__icontains=search_str, user=request.user) |
            Q(description__icontains=search_str, user=request.user)
        )

        # Adjust the serializer to include the category name
        data = [
            {
                "id": expense.id,
                "amount": expense.amount,
                "date": expense.date,
                "description": expense.description,
                "category": expense.category.name  # Access the category name here
            } 
            for expense in expenses
        ]

        # Return the modified data as JSON
        return JsonResponse(data, safe=False)

def expense_catetory_summary(request):
    todays_date = datetime.date.today()
    six_months_age = todays_date - datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(user = request.user, date__gte=six_months_age, date__lte=todays_date)
    final_rep = {}
    
    def get_category(expense):
        return expense.category
    
    Category_list = list(set(map(get_category, expenses)))
    
    def get_expenses_category_amount(category):
        amount = 0
        filtered_bt_category = expenses.filter(category=category)
        
        for item in filtered_bt_category:
            amount += item.amount
        return amount
    
    for e in expenses:
        for c in Category_list:
            final_rep[str(c)] = get_expenses_category_amount(c)
            
            
    return JsonResponse({'expense_category_data': final_rep}, safe=False)

def stats_view(request):
    return render(request, 'expenses/stats.html')

def export_csv(request):
    res = HttpResponse(content_type = 'text/csv')
    res['Content-Disposition'] = 'attachment; filename=Expenses_' +  str(datetime.datetime.now()) + '.csv'
    
    writer = csv.writer(res)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])
    
    expenses = Expense.objects.filter(user=request.user)
    
    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])
        
    return res

def export_excel(request):
    res = HttpResponse(content_type='application/ms-excel')
    res['Content-Disposition'] = 'attachment; filename=Expenses_' + str(datetime.datetime.now()) + '.xls'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    
    row_num = 0
    
    # Style for the header row
    font_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    font_style.font = font
    
    columns = ['Amount', 'Description', 'Category', 'Date']
    
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
        
    # Style for the rest of the rows
    font_style = xlwt.XFStyle()
    
    rows = Expense.objects.filter(user=request.user).values_list('amount', 'description', 'category', 'date')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    
    wb.save(res)
    return res

from weasyprint import HTML

def export_pdf(request):
    res = HttpResponse(content_type='application/pdf')
    res['Content-Disposition'] = 'inline; filename=Expenses_' + str(datetime.datetime.now()) + '.pdf'
    res['Content-Transfer-Encoding'] = 'binary'

    expenses = Expense.objects.filter(user=request.user)
    total = expenses.aggregate(Sum('amount'))

    html_string = render_to_string('expenses/pdf.html', {'expenses': expenses, 'total': total})
    html = HTML(string=html_string)
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output.seek(0)
        res.write(output.read())

    return res
        
    