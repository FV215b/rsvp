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
]
