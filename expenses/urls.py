from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name='expenses'),
    path('add-expenses', views.add_expenses, name='add-expenses'),
    path('stats', views.stats_view, name='stats'),
    path('export-csv', views.export_csv, name='export-csv'),
    path('export-excel', views.export_excel, name='export-excel'),
    path('export-pdf', views.export_pdf, name='export-pdf'),
    path('expense-category', views.expense_catetory_summary, name='expense-category'),
    path('search-expenses', csrf_exempt(views.search_expenses), name='search-expenses'),
    path('edit-expenses/<int:id>', views.edit_expenses, name='edit-expenses'),
    path('delete-expenses/<int:id>', views.delete_expenses, name='delete-expenses'),
]
