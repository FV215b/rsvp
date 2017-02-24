from django.shortcuts import render
from rsvpapp.forms import RegisterForm
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# Create your views here.

def register(request, template_name):
    if request.method == "POST":
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            from django.contrib.auth import authenticate, login
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password1'))
            login(request, user)
            return HttpResponseRedirect(reverse('homepage'))
    else:
        form = RegisterForm()

    #request_context = RequestContext(request)
    #request_context.push({'form': form});
    return render(request, template_name, {'form': form})

def homepage(request, template_name):
    return render(request, template_name)
