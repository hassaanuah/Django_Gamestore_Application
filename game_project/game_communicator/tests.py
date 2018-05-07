"""Includes unit tests for the game_communicator app, should be executed from the project root
   with the command 'python manage.py test game_communicator'"""

from django.contrib.auth.models import User
from django.test import TestCase, Client
from game_server.models import PurchasedGames

class CommunicatorGetTest(TestCase):
    """Test the Communicator GET methods"""
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_retrieving_game_state(self):
        """Tests that the communicator retrieves the same data as in the database"""
        test_user = User.objects.get(username="player")
        self.client.force_login(test_user)
        response = self.client.get('/gamecommunicator?msgtype=load&gameid=2')
        purchases_entry = PurchasedGames.objects.get(user_id=test_user, game=2)

        self.assertEqual(response.content, purchases_entry.game_state.encode('utf-8'))

class CommunicatorPostTest(TestCase):
    """Test the Communicator POST methods"""
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()
        self.test_user = User.objects.get(username="player")
        self.client.force_login(self.test_user)

    def test_updating_score(self):
        """Tests that the game communicator properly stores a new high score in database"""
        message = {'msgtype': 'score', 'gameid': '2', 'score': '400'}
        response = self.client.post('/gamecommunicator', message)
        purchases_entry = PurchasedGames.objects.get(user_id=self.test_user, game=2)

        self.assertEqual(response.content, 'Score submitted'.encode('utf-8'))
        self.assertEqual(purchases_entry.high_score, 400)

    def test_updating_game_state(self):
        """Tests that the game communicator properly stores a new game state in database"""
        message = {'msgtype': 'save', 'gameid': '2',
                   'gamestate': '{\"playerItems\":[\"A rock\"],\"score\":100}'}
        response = self.client.post('/gamecommunicator', message)
        purchases_entry = PurchasedGames.objects.get(user_id=self.test_user, game=2)

        self.assertEqual(response.content, 'Game state saved'.encode('utf-8'))
        self.assertEqual(purchases_entry.game_state,
                         '{\"playerItems\":[\"A rock\"],\"score\":100}')
