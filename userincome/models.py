from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.
        
        
        
class Source(models.Model):
    name = models.CharField( max_length=250)
        
        
    def __str__(self):
        return self.name
        
class UserIncome(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    description = models.TextField(max_length=250)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    date = models.DateTimeField(default=now)
    
    def __str__(self) -> str:
        return f'{self.user.username}'
    
    class Meta:
        ordering = ['-date']

        