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
    start_time = models.DateTimeField('event start time', null = True)
    address = models.CharField(max_length=100)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Permission')
    plus_one_allowed = models.BooleanField(default=False)

    def __str__(self) :
        return self.title

    def get_questions(self):
        return self.question_set.all()

#q_type: 0-multiple choice, 1-single choice, 2-text answer
class Question(models.Model):
    MULTICHOICE = 0
    SINGLECHOICE = 1
    TEXT = 2
    QUESTION_TYPE_CHOICES = (
        (MULTICHOICE, "multiple choice"),
        (SINGLECHOICE, "single choice"),
        (TEXT, "text question"),
    )
    qid = models.CharField(max_length=50, primary_key=True)
    q_type = models.DecimalField(max_digits=1, decimal_places=0, default=MULTICHOICE, choices=QUESTION_TYPE_CHOICES)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null = True, related_name="question")
    question = models.CharField(max_length=50)
    visibility = models.BooleanField(default=True)
    changeable = models.BooleanField(default=True)

    def __str__(self) :
        return self.question

    def get_choices(self):
        return self.choice_set.all()

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choice")
    choice = models.CharField(max_length=20)
    user = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self) :
        return self.choice

    def choosen_users(self):
        return self.user_set.all()

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) :
        return self.choice

    def choosen_users(self):
        return self.user_set.all()

#0-owner, 1-vendor, 2-guest
class Permission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    permission = models.DecimalField(max_digits=1, decimal_places=0)
    attend = models.BooleanField(default=True)
    plus_one = models.BooleanField(default=False)

    def __str__(self) :
        return '%s %s' % (self.user.username, self.event)

class PKManagement(models.Model):
    model_name = models.CharField(max_length=20)
    max_number = models.DecimalField(max_digits=10, decimal_places=0, default=0)
