
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    category_name = models.CharField(max_length=100)
    category_code = models.CharField(max_length=20)

    def __str__(self):
        return self.category_name


class Event(models.Model):
    event_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    venue = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.event_name


class UserProfile(models.Model):

    user = models.OneToOneField(User,on_delete=models.CASCADE)

    phone=models.CharField(max_length=10)

    college=models.CharField(max_length=150)

    profile_image=models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username



class EventMember(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    college = models.CharField(max_length=100)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    qr_code=models.ImageField(
        upload_to="qrcodes/",
        blank=True,
        null=True
    )

    attended=models.BooleanField(default=False)

    def __str__(self):
        return self.name


class EventWishList(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.event.event_name}"

from django.utils import timezone

class Notification(models.Model):

    title = models.CharField(max_length=200)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title