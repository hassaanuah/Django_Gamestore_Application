"""Commonly used functions for game_communicator"""

from django.core.exceptions import ObjectDoesNotExist
from game_server.models import GameList, PurchasedGames

def get_purchased_game_instance(user, gameid):
    """Returns the Purhcased Game instance if it exists, otherwise returns None"""
    try:
        purchased_games_obj = PurchasedGames.objects.select_related().filter(user_id=user)
        purchased_games_obj = purchased_games_obj.filter(game=GameList.objects.get(pk=gameid))
        return purchased_games_obj[0]
    except ObjectDoesNotExist:
        return None
