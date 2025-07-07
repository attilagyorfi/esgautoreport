# accounts/signals.py
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Ez a jelzés automatikusan létrehoz egy UserProfile-t,
    amikor egy új User jön létre.
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Ez a jelzés automatikusan elmenti a profilt,
    amikor a User objektum mentésre kerül.
    """
    instance.profile.save()