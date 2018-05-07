"""Includes all game_server URLs"""

from django.conf.urls import url
from django.views.generic.base import TemplateView
from game_server import views

urlpatterns = [
    url(r'^register$', views.register, name='register'),
    url(r'^login$', views.login, name='login'),
    url(r'^resetpassword$', views.resetpassword, name='resetpassword'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^store$', views.store, name='store'),
    url(r'^boughtgames$', views.boughtgames, name='boughtgames'),
    url(r'^gamestorepage/(?P<gameid>\d+)$', views.gamestorepage, name='gamestorepage'),
    url(r'^playgame/(?P<gameid>\d+)$', views.playgame, name='playgame'),
    url(r'^buygame$', views.buygame, name='buygame'),
    url(r'^addgames$', views.addgames, name='addgames'),
    url(r'^accountdetails$', views.accountdetails, name='accountdetails'),
    url(r'^mygames$', views.mygames, name='mygames'),
    url(r'^deletegame/(?P<game_id>\d+)$', views.deletegame, name='deletegame'),
    url(r'^activategame/(?P<game_id>\d+)$', views.activategame, name='activategame'),
    url(r'^deactivategame/(?P<game_id>\d+)$', views.deactivategame, name='deactivategame'),
    url(r'^editgame/(?P<game_id>\d+)$', views.editgame, name='editgame'),
    url(r'^gamestats/(?P<game_id>\d+)$', views.gamestats, name='gamestats'),
    url(r'^user_verification/(?P<verification_bytes>[\w|\W]+)/$', views.verification_email,
        name='verification_email'),
    url(r'^reset_password/(?P<verification_bytes>[\w|\W]+)/$', views.reset_password,
        name='reset_password'),
    url(r'^social_registration', views.social_registration, name='social_registration'),
    url(r'^robots.txt$', TemplateView.as_view(template_name='game_server/robots.txt',
                                              content_type='text/plain')),
    url(r'^$', views.home, name='home'),
]
