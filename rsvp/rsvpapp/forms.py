from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm, modelformset_factory
from django.contrib.auth.models import User
from rsvpapp.models import Event
from rsvpapp.models import Question
from rsvpapp.models import Choice

class RegisterForm(UserCreationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2", "first_name", "last_name")
        widgets = {
            'username': forms.EmailInput(),
        }
    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'start_time', 'address', 'plus_one_allowed']
        widgets = {
            'start_time': forms.DateTimeInput()
        }

class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'visibility']
        widgets = {
            'visibility': forms.CheckboxInput()
        }

class AddUserForm(forms.Form):
    email = forms.EmailField(required=False)
