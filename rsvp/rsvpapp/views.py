import string
from django.forms.models import model_to_dict
from django.template import RequestContext
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from rsvpapp.forms import EventForm
from rsvpapp.forms import RegisterForm
from rsvpapp.forms import QuestionForm
from django.forms import inlineformset_factory
from rsvpapp.models import Event
from rsvpapp.models import Permission
from rsvpapp.models import Question
from rsvpapp.models import Choice

# Create your views here.
ChoiceFormSet = inlineformset_factory(Question, Choice, fields=('choice',), extra=1)

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

    context = {'form': form}
    return render(request, template_name, context)

def homepage(request, template_name):
    next_event_id = (request.user.username + "_" + str(request.user.event_set.count() + 1))\
    .replace("@", "_")\
    .replace(".", "_");
    events = request.user.event_set.all().extra(order_by = ['-permission__permission__gt'])
    context = {'next_event_id': next_event_id, 'events': events}
    return render(request, template_name, context)

def create_event(request, template_name, new_eid):
    event = get_object(Event, new_eid)
    if event is None:
        event = Event.objects.create(pk = new_eid)
    if request.method == "POST":
        form = EventForm(data=request.POST, \
        instance=event, \
        initial=model_to_dict(event))
        if form.is_valid():
            form.save()
            permission = Permission(user=request.user, event=event, permission=0)
            permission.save()
    else:
        form = EventForm(instance=event, \
        initial=model_to_dict(event))
    new_qid = new_eid + "_" + str(event.question_set.count() + 1);
    context = {'form': form, 'new_eid': new_eid, 'new_qid': new_qid}
    return render(request, template_name, context)

def add_question(request, template_name, new_eid, new_qid):
    event = get_object(Event, new_eid)
    question = get_object(Question, new_qid)
    if question is None:
        question = Question.objects.create(pk=new_qid)
    if request.method == "POST":
        question_form = QuestionForm(data=request.POST, \
        instance=question, \
        initial=model_to_dict(question))
        choice_formset = ChoiceFormSet(request.POST, \
        instance=question, \
        initial=question.choice_set.all().values())
        if question_form.is_valid() and choice_formset.is_valid():
            question_form.save()
            choice_formset.save()
            event.save()
            event.question_set.add(question)
    else:
        question_form = QuestionForm(instance=question,\
        initial=model_to_dict(question))
        choice_formset = ChoiceFormSet(instance=question,\
        initial=question.choice_set.all().values())

    context = {'question_form': question_form, 'choice_formset': choice_formset, 'new_qid': new_qid, 'new_eid': new_eid}
    return render(request, template_name, context)

def get_object(Model, value):
    try:
        target = Model.objects.get(pk = value)
    except Model.DoesNotExist:
        target = None
    return target
