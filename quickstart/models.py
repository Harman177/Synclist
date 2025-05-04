from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
 
class QuickSession(models.Model):
     name = models.CharField(max_length=100)
     created_at = models.DateTimeField(auto_now_add=True)
     data = models.JSONField(default=dict)
     
     def is_expired(self):
         return timezone.now() > self.created_at + timezone.timedelta(hours=24)