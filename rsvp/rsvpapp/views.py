import string
from django.forms.models import model_to_dict
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django import forms
from rsvpapp.forms import EventForm
from rsvpapp.forms import RegisterForm
from rsvpapp.forms import QuestionForm
from django.forms import inlineformset_factory
from rsvpapp.models import Event
from rsvpapp.models import Permission
from rsvpapp.models import Question
from rsvpapp.models import Choice

# Create your views here.
ChoiceFormSet = inlineformset_factory(Question, Choice, fields=('choice',), extra=10)

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
    permissions = request.user.permission_set.all().select_related('event')
    context = {'next_event_id': next_event_id, 'permissions': permissions}
    return render(request, template_name, context)

def create_event(request, template_name, new_eid):
    event = get_object(Event, new_eid)
    if event is None:
        event = Event.objects.create(pk = new_eid)
    questions = event.question.all()
    question_list = get_question_list(questions)

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
    new_qid = new_eid + "_" + str(event.question.count() + 1);
    context = {'form': form, 'questions': question_list, 'new_eid': new_eid, 'new_qid': new_qid}
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
        choice_formset = ChoiceFormSet(data=request.POST, \
        instance=question, \
        initial=question.choice.all().values())
        if question_form.is_valid() and choice_formset.is_valid():
            question_form.save()
            choice_formset.save()
            event.save()
            event.question.add(question)
            permission = Permission(user=request.user, event=event, permission=0)
            permission.save()
    else:
        question_form = QuestionForm(instance=question,\
        initial=model_to_dict(question))
        choice_formset = ChoiceFormSet(instance=question,\
        initial=question.choice.all().values())

    context = {'question_form': question_form, 'choice_formset': choice_formset, 'new_qid': new_qid, 'new_eid': new_eid}
    return render(request, template_name, context)

def view_event(request, eid, permission):
    context = {'eid': eid, 'permission': permission}
    print(type(permission))
    if permission == '0':
        return view_event_as_owner(request, 'view_event_as_owner.html', context)
    elif permission == '1':
        return view_event_as_vendor(request, 'view_event_as_vendor.html', context)
    elif permission == '2':
        return view_event_as_guest(request, 'view_event_as_guest.html', context)
    else:
        raise Http404

def view_event_as_owner(request, template, context):
    eid = context['eid']
    event = get_object_or_404(Event, pk = eid)
    questions = event.question.all()
    question_list = get_question_list(questions)
    event_data = dict([('event', event), ('questions', question_list)])
    context['event_data']=event_data
    return render(request, template, context)

def get_question_list(questions):
    question_list = []
    for question in questions:
        question_list.append(dict([('question', question.question), ('choice', question.choice.all())]))
    return question_list

def get_object(Model, value):
    try:
        target = Model.objects.get(pk = value)
    except Model.DoesNotExist:
        target = None
    return target
