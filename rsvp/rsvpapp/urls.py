from django.conf.urls import url, include

from . import views
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/rsvpapp/login'}, name='logout'),
    url(r'^register', views.register, {'template_name': 'register.html'}, name='register'),
    url(r'^homepage', views.homepage, {'template_name': 'homepage.html'}, name='homepage'),
    url(r'^create_event/(?P<new_eid>\w+)', views.create_event, {'template_name': 'create_event.html'}, name='create_event'),
    url(r'^add_question/(?P<new_eid>\w+)/(?P<new_qid>\w+)', views.add_question, {'template_name': 'add_question.html'}, name='add_question'),
    url(r'^view_event/(?P<eid>\w+)/(?P<permission>\d)', views.view_event, name='view_event'),
    url(r'^add_vendor/(?P<eid>\w+)/(?P<permission>\w+)', views.add_user, {'template_name': 'add_user_to_event.html'}, name='add_vendor'),
    url(r'^add_guest/(?P<eid>\w+)/(?P<permission>\w+)', views.add_user, {'template_name': 'add_user_to_event.html'}, name='add_guest'),
    url(r'^add_owner/(?P<eid>\w+)/(?P<permission>\w+)', views.add_user, {'template_name': 'add_user_to_event.html'}, name='add_owner'),
    url(r'^remove_event/(?P<eid>\w+)', views.remove_event, name='remove_event'),
    url(r'^remove_question/(?P<eid>\w+)/(?P<qid>\w+)', views.remove_question, name='remove_question'),
    url(r'^remove_permission/(?P<eid>\w+)/(?P<username>[\s\S]*?)/(?P<permission>\d)', views.remove_permission, name='remove_permission'),
    url(r'^choice_detail/(?P<cid>\d+)/(?P<eid>\w+)/(?P<permission>\d)', views.choice_detail, {'template_name': 'choice_detail.html'}, name='choice_detail'),
    url(r'^no_permission/', views.no_permission, name='no_permission'),
    url(r'^add_answer/(?P<eid>\w+)', views.add_answer, name='add_answer'),
    url(r'^question_changeable/(?P<eid>\w+)', views.question_changeable, name='question_changeable'),
]
