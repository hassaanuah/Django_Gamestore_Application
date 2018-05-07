"""Helper functions for commonly used actions in game_server"""

from hashlib import md5
from django.core.exceptions import ObjectDoesNotExist
from game_server.models import PurchasedGames

def user_owns_game(user, gameid):
    """Returns True if user owns the game, False otherwise"""
    purchased_games = PurchasedGames.objects.select_related().filter(user_id=user)
    for purchased_game in purchased_games:
        if purchased_game.game.pk == int(gameid):
            return True
    return False

def create_checksum(parameters, pid, sid, amount, secret_key):
    """Returns the calculated checksum over the provided fields"""

    checksumstr = parameters.format(pid, sid, amount, secret_key)
    md5hash = md5(checksumstr.encode("ascii"))
    return md5hash.hexdigest()

def usertype_exists(user):
    """Used to detect users logged in via 3rd party authentication that have not specified
    their user type"""
    try:
        if user.type:
            return True
        return False
    except ObjectDoesNotExist:
        return False
