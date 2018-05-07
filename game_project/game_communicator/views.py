"""Handles all the logic and views for playing games through the service"""

from django.http import HttpResponse, HttpResponseBadRequest
from game_communicator.helperfunctions import get_purchased_game_instance

def gamecommunicator(request):
    """This view is used to update and retrieve stored game information"""
    if request.method == 'POST':
        msg_type = request.POST.get("msgtype", None)
        game_instance = get_purchased_game_instance(request.user, request.POST['gameid'])
        if msg_type == "score":
            game_instance.update_score(int(request.POST['score']))
            return HttpResponse('Score submitted')
        elif msg_type == "save":
            game_instance.update_game_state(request.POST['gamestate'])
            return HttpResponse('Game state saved')
        return HttpResponseBadRequest()
    else:
        msg_type = request.GET.get("msgtype", None)
        if msg_type == "load":
            game_instance = get_purchased_game_instance(request.user, request.GET['gameid'])
            if game_instance:
                return HttpResponse(game_instance.game_state)
            return HttpResponse("")
        return HttpResponseBadRequest()
