from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.

class Category(models.Model):
        name = models.CharField( max_length=250)
        
        
        def __str__(self):
            return self.name
        
        class Meta:
            verbose_name_plural = 'Categories'
        
        
        
        
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    description = models.TextField(max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateTimeField(default=now)
    
    def __str__(self) -> str:
        return f'{self.user.username}'
    
    class Meta:
        ordering = ['-date']

