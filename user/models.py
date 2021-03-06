from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from django.db.models import Sum

from reportedPhotos.models import ReportedPhotos
from photo.models import Photo
from contest.models import Tag
import allauth
from django.contrib.auth.models import Permission

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Username")
    location = models.CharField(max_length=30, blank=True, verbose_name="Location")
    email_verified = models.BooleanField(blank=False, default=False, verbose_name='E-mail verification')
    achievements = models.TextField(blank=True)
    aboutme = models.TextField(blank=True)
    is_premium = models.BooleanField(blank=False, default=False, verbose_name='Premium status')
    reported_photos = models.ManyToManyField(ReportedPhotos, blank=True)
    photos_will_be_shown = models.ManyToManyField(Photo, blank=True, related_name='photos_will_be_shown')
    all_time_average = models.FloatField(blank=False, default=0.00, verbose_name='All Time Average')
    voted_x_times = models.IntegerField(blank=False, default=0, verbose_name='X kere oylandı (bütün fotoğrafları)')
    prefered_tags = models.ManyToManyField(Tag, blank=True)
    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('tr', 'Türkçe'),
    )
    languagePreference = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

    #Eğer sosyal hesap ise email onayı gerekmesin. Onaylanmış kabul ediyoruz.
    if instance.socialaccount_set.all:
        instance.profile.email_verified = True
        instance.profile.save()

        # Giving permissions
        permission1 = Permission.objects.get(name='Can add new photos?')
        permission2 = Permission.objects.get(name='Can vote photos?')
        instance.user_permissions.add(permission1)
        instance.user_permissions.add(permission2)


def get_name_or_username(self):
    if not self.first_name:
        return self.username
    elif not self.last_name:
        return self.first_name
    else:
        return self.first_name + ' ' + self.last_name


User.add_to_class('get_name_or_username', get_name_or_username)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    msg = models.TextField()
    read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ('-id', )
        get_latest_by = ('id')

    def __str__(self):
        return self.msg


@receiver(post_save, sender=User)
def create_welcoming_notification(sender, instance, created, **kwargs):
    if created:
        welcome = Notification(user=instance, msg="Thank you for joining Photash " + str(instance) + '!')
        welcome.save()

        #Sosyal hesap değilse (normal hesap ise) email gönderdik bildirimi oluşturuyoruz
        if not instance.socialaccount_set.all:
            please_verify = Notification(user = instance, msg="We have sent a confirmation link to " + str(instance.email) + "\n You can explore the photos but you can't vote or upload a photo until you verify your account.")
            please_verify.save()







