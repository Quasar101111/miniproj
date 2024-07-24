# users/models.py

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    USER_TYPES = (
        ('lessor', 'Lessor'),
        ('tenant', 'Tenant'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=6, choices=USER_TYPES)

    def __str__(self):
        return f'{self.user.email} Profile'
    
class Lessor(models.Model):
      
        lessor_id = models.AutoField(primary_key=True)
        lessor_name = models.CharField(max_length=50)
        email = models.EmailField(max_length=50)
        contact_number = models.CharField(max_length=50)
        photo = models.ImageField(upload_to='lessor_photos/')

        def __str__(self):
            return self.lessor_name
        
        