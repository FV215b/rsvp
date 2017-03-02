import string
from django.forms.models import model_to_dict
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django import forms
from rsvpapp.forms import EventForm, RegisterForm, QuestionForm, AddUserForm
from django.forms import inlineformset_factory
from rsvpapp.models import Event, Permission, Question, Choice
from django.contrib.auth.decorators import login_required

# Create your views here.
ChoiceFormSet = inlineformset_factory(Question, Choice, fields=('choice',), extra=1)
User = get_user_model()

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

@login_required
def homepage(request, template_name):
    next_event_id = (request.user.username + "_" + str(request.user.event_set.count() + 1))\
    .replace("@", "_")\
    .replace(".", "_");
    permissions = request.user.permission_set.all().select_related('event')
    context = {'next_event_id': next_event_id, 'permissions': permissions}
    return render(request, template_name, context)

@login_required
def create_event(request, template_name, new_eid):
    event = get_object(Event, new_eid)
    if event is None:
        event = Event.objects.create(pk = new_eid)
        event.save()
    new_qid = new_eid + "_" + str(event.question.count() + 1);
    questions = event.question.all()
    question_list = get_question_list(questions)
    members = event.members.all()
    owners = members.filter(permission__permission = 0)
    vendors = members.filter(permission__permission = 1)
    guests = members.filter(permission__permission = 2)

    guest_form=AddUserForm()
    vendor_form=AddUserForm()
    owner_form=AddUserForm()
    if request.method == "POST":
        form = EventForm(data=request.POST, instance=event)
        if form.is_valid():
            form.save()
            permission = Permission(user=request.user, event=event, permission=0)
            permission.save()
    else:
        form = EventForm(instance=event, data = model_to_dict(event))

    context = {'form': form, \
    'owner_form': owner_form, \
    'vendor_form': vendor_form,\
    'guest_form': guest_form, \
    'owners': owners, \
    'vendors': vendors, \
    'guests': guests, \
    'questions': question_list, \
    'new_eid': new_eid, \
    'new_qid': new_qid}
    return render(request, template_name, context)

@login_required
def add_question(request, template_name, new_eid, new_qid):
    event = get_object(Event, new_eid)
    question = get_object(Question, new_qid)
    if question is None:
        question = Question.objects.create(pk=new_qid)
    if request.method == "POST":
        question_form = QuestionForm(data=request.POST, instance=question)
        choice_formset = ChoiceFormSet(data=request.POST, instance=question, prefix='choices')
        if question_form.is_valid() and choice_formset.is_valid():
            question_form.save()
            choice_formset.save()
            event.question.add(question)
    else:
        question_form = QuestionForm(instance=question)
        choice_formset = ChoiceFormSet(instance=question, prefix='choices')
    context = {'question_form': question_form, 'choice_formset': choice_formset, 'new_qid': new_qid, 'new_eid': new_eid}
    return render(request, template_name, context)

@login_required
def view_event(request, eid, permission):
    context = {'eid': eid, 'permission': permission}
    if permission == '0':
        return view_event_as_owner(request, 'view_event_as_owner.html', context)
    elif permission == '1':
        return view_event_as_vendor(request, 'view_event_as_vendor.html', context)
    elif permission == '2':
        return view_event_as_guest(request, 'view_event_as_guest.html', context)
    else:
        raise Http404

@login_required
def add_user(request, template_name, eid):
    user_exist = 0
    if request.method == "POST":
        add_user_form=AddUserForm(request.POST)
        if add_user_form.is_valid():
            add_user_id = add_user_form.cleaned_data['email']
            add_user=get_user(add_user_id)
            if add_user is None:
                messages.info(request, 'User does not exist')
            else:
                user_exist = 1
                event = get_object(Event, eid)
                if event is None:
                    event = Event.objects.create(pk = eid)
                    event.save()
                    permission = Permission(user=request.user, event=event, permission=0)
                    permission.save()
                add_user_permission = Permission(user=add_user, event=event, permission=int(request.POST.get("permission")))
                add_user_permission.save()
    context = {'eid': eid, 'user_exist': user_exist}
    return render(request, template_name, context)

def view_event_as_owner(request, template, context):
    eid = context['eid']
    event = get_object_or_404(Event, pk = eid)
    members = event.members.all()
    owners = members.filter(permission__permission = 0)
    vendors = members.filter(permission__permission = 1)
    guests = members.filter(permission__permission = 2)
    guest_form=AddUserForm()
    vendor_form=AddUserForm()
    owner_form=AddUserForm()
    questions = event.question.all()
    question_list = get_question_list(questions)
    event_data = dict([('event', event), ('questions', question_list)])
    context['event_data']=event_data
    context['owners']=owners
    context['vendors']=vendors
    context['guests']=guests
    context['owner_form']=owner_form
    context['guest_form']=guest_form
    context['vendor_form']=vendor_form
    return render(request, template, context)

def view_event_as_guest(request, template_name, context):
    eid = context['eid']
    event = get_object_or_404(Event, pk=eid)
    questions = event.question.all()
    effective_questions = questions.filter(visibility=True).filter(changeable=True) 
    question_list = get_question_list(effective_questions)
    event_data = dict([('event', event), ('questions', question_list)])
    context['event_data'] = event_data
    
    checked_choice = dict([('event', event), ('choices', get_checked_list(request.user, effective_questions))])
    context['checked_choice'] = checked_choice
    return render(request, template_name, context)

def add_answer(request, eid):
    if request.method == "POST":
        event = get_object_or_404(Event, pk=eid)
        names = request.POST
        questions = event.question.all()
        effective_questions = questions.filter(visibility=True).filter(changeable=True)
        for question in effective_questions:
            choices = question.choice.all()
            for choice in choices:
                choice_name = event.title + "#" + choice.question.question + "#" + choice.choice + "#1"
                if choice_name in names:
                    choice.user.add(request.user)
                    choice.save()
                elif choice.user.filter(username=request.user.username).exists():
                    choice.user.remove(request.user)
                    choice.save()
    return HttpResponseRedirect(reverse('homepage'))

def get_checked_list(user, questions):
    checked_list = []
    for question in questions:
        for choice in question.choice.all():
            if choice.user.filter(username=user.username).exists():
                checked_list.append(choice)
    return checked_list

def get_question_list(questions):
    question_list = []
    for question in questions:
        question_list.append(dict([('question', question), ('choice', question.choice.all())]))
    return question_list

def get_object(Model, value):
    try:
        target = Model.objects.get(pk = value)
    except Model.DoesNotExist:
        target = None
    return target

def get_user(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    return user
