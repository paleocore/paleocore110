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
    print("line 14")
    if created:
        print("line 16")
        UserInstitution.objects.create(user=instance, institution="None")
        try:
            print("line 19")
            instance.userinstitution.save()
            print(instance.userinstitution.institution)
        except Exception as e:
            print("line 22")
            pass