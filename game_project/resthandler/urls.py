from django.conf.urls import url

from resthandler import views

urlpatterns = [

    url(r'^rest_view/(?P<id>\d+)$', views.rest_handle, name='rest_handle'),
    url(r'^rest_view', views.rest_handle, {'id':False}, name='rest_handle'),

]