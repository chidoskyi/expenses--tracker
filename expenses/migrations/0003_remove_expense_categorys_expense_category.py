# Generated by Django 5.0.6 on 2024-07-11 18:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0002_remove_expense_category_expense_categorys'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expense',
            name='categorys',
        ),
        migrations.AddField(
            model_name='expense',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='expenses.category'),
        ),
    ]