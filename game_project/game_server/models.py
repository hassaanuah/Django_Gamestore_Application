from django.db import models
from django.contrib.auth.models import User

class UserType(models.Model):
    '''
    Table Defines if an User is a Player or a Developer.
    '''
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, related_name='type')
    developer = models.BooleanField()
    verification_bytes = models.CharField(max_length=64)

    def __str__(self):
        if self.developer:
            return self.user_id.username + " - " + "Developer"
        return self.user_id.username + " - " + "Player"

class GameList(models.Model):
    '''
    Table maps the developer with the games. All games added by developers are shows in this table
    This table includes the following details:
        > ID of user who uploaded the game
        > Name of game
        > Category of game
        > Description of game
        > Price of game set to maximum 7 digits with 2 decimal digits. Example is 64534.87
        > Image (screenshot) of the game for store page and store listing
        > URL for the game to load it to iframe
        > Number of times this game has been purchased
        > All time high score of game
        > Time added for release date
    '''
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    game_name = models.CharField(max_length=128, unique=True)
    category = models.CharField(max_length=64)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to='game_images/')
    url = models.CharField(max_length=512)
    num_of_purchases = models.PositiveIntegerField(default=0)
    high_score = models.IntegerField(blank=True, default=0, null=True)
    time_added = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.game_name

    def increment_purchases(self):
        """Used to increment the purchases, automatically called when a new PurchasedGame instance
           is created"""

        self.num_of_purchases += 1
        self.save()

    def update_score(self, score):
        """Increments the global high score. Should be called via the function with the same
           name in PurchasedGame"""

        if score > self.high_score:
            self.high_score = score
            self.save()


class PurchasedGames(models.Model):
    '''
    Table maps the Player with his purchased games.
    This table includes the following details:
        > ID of user who purchased the game
        > ID of the game purchased
        > High score of this user for this game
        > Purchase time for developer listing
    '''
    user_id = models.ForeignKey(User)
    game = models.ForeignKey(GameList)
    high_score = models.IntegerField(blank=True, default=0)
    game_state = models.TextField(blank=True, default="")
    purchase_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_id.username + " - " + self.game.game_name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """If the model has no pk (yet) it has not been previously saved, which means it is a
           new purchase and game purchases must be incremented"""

        if not self.pk:
            self.game.increment_purchases()

        super(PurchasedGames, self).save(force_insert, force_update, using, update_fields)

    def update_score(self, score):
        """Used to update the stored score. Checks if higher than previous and also tries updating
           the global score"""

        if score > self.high_score:
            self.high_score = score
            self.game.update_score(score)
            self.save()

    def update_game_state(self, game_state):
        """Used for storing a game state in the game instance"""

        self.game_state = game_state
        self.save()
