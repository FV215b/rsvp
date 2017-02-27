from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
# Create your models here.

#class User(AbstractUser):
#    username = models.EmailField(primary_key=True)

class Event(models.Model):
    eid = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    start_time = models.DateTimeField('event start time', null = True, blank=True)
    address = models.CharField(max_length=100)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Permission')

    def __str__(self) :
        return self.title

    def get_questions(self):
        return self.question_set.all()

class Question(models.Model):
    qid = models.CharField(max_length=50, primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null = True)
    question = models.CharField(max_length=50)
    visibility = models.BooleanField(default=True)
    changeable = models.BooleanField(default=True)

    def __str__(self) :
        return self.question

    def get_choices(self):
        return self.choice_set.all()

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.CharField(max_length=20)
    user = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self) :
        return self.choice

    def choosen_users(self):
        return self.user_set.all()

#0-owner, 1-vendor, 2-guest
class Permission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    permission = models.DecimalField(max_digits=1, decimal_places=1)
    attend = models.BooleanField(default=True)

    def __str__(self) :
        return '%s %s' % (self.user.username, self.event)
