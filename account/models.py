from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserInstitution(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.CharField(max_length=128)
    email_confirmed = models.BooleanField(default=False)

@receiver(post_save, sender=User)
def update_user_institution(sender, instance, created, **kwargs):
    if created:
        UserInstitution.objects.create(user=instance, institution="None")
        try:
            instance.userinstitution.save()
        except Exception as e:
            pass