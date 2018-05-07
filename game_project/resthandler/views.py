import base64
from django.http import HttpResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from game_server.models import GameList
# Create your views here.

@csrf_exempt
def rest_handle(request, id):
    '''
    Function to handle REST quesries. A sample query with authentication is:
    http --auth username:password http://10.0.2.15:8000/rest_view/8
    :or
    http --auth username:password DELETE http://10.0.2.15:8000/rest_view/8
    or
    http http://10.0.2.15:8000/rest_view
    or
    http --auth username:password http://10.0.2.15:8000/rest_view
    It would for retrieving games for guest user and registered user.
    Registered user needs to provide his credentials to delete game or view complete details of game
    Guest user (without authentication) can see all games or selected games but only limited details
    '''
    decoded_credentials=None
    user = None
    if 'HTTP_AUTHORIZATION' in request.META:
        auth_header = request.META['HTTP_AUTHORIZATION']
        encoded_credentials = auth_header.split(' ')[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
        user = authenticate(username=decoded_credentials[0], password=decoded_credentials[1])
    if request.method == "DELETE":
        if id:
            if user:
                try:
                    game_entry = GameList.objects.get(pk=id, user_id=user)
                    if game_entry.num_of_purchases == 0:
                        game_entry.image.delete(save=True)
                        game_entry.delete()
                        data = "Success"
                    else:
                        game_entry.active = False
                        game_entry.save()
                        data = game_entry.game_name + ' has been deactivated and not deleted because it has been purchases ' + str(game_entry.num_of_purchases) + ' times.'
                except:
                    data = "Authentication Unsuccessful"
            else:
                data = "Authentication Unsuccessful"
        else:
            data="ID is not provided to delete"
    elif request.method == "GET":
        if user or id:
            if user and id:
                data = GameList.objects.all().filter(pk=id, user_id=user.id)
                data = serializers.serialize('json', data)
            elif user:
                data = GameList.objects.all().filter(user_id=user.id)
                data = serializers.serialize('json', data)
            elif id:
                data = GameList.objects.all().filter(pk=id)
                data = serializers.serialize('json', data, fields=('game_name', 'category', 'description'))
        else:
            data = GameList.objects.all()
            data = serializers.serialize('json', data, fields=('game_name', 'category', 'description'))
    else:
        data = "Not correct Method. Invalid HTTP request"
    return HttpResponse(data, content_type='application/json')