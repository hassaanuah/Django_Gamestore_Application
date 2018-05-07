"""UnitTests for the application, should be executed from the project root with the command
   'python manage.py test game_server'"""

import glob
import os
import html5lib
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, Client
from django.template.loader import render_to_string
from selenium.webdriver.firefox.webdriver import WebDriver
from game_server.models import GameList, UserType, PurchasedGames
from game_communicator.helperfunctions import get_purchased_game_instance

class HTMLValidity(TestCase):
    """Tests that views produce valid HTML5"""

    def setUp(self):
        self.parser = html5lib.HTMLParser(strict=True)

    def test_all_templates(self):
        """Tests all templates for validity (rendered without context)"""
        for path in glob.glob('game_server/templates/game_server/*.html'):
            template = os.path.basename(path)
            document = render_to_string("game_server/" + template)
            self.assertRaises(Exception, self.parser.parse(document))

    def test_home_view(self):
        """Renders the home view with a simple test message"""
        document = render_to_string("game_server/home.html", {'message' : "Test message"})
        self.assertRaises(Exception, self.parser.parse(document))

    def test_store_view(self):
        """Renders the store view"""

        #Test an empty store
        document = render_to_string("game_server/store.html", {'games': GameList.objects.all()})
        self.assertRaises(Exception, self.parser.parse(document))

        #Test a store with some games
        game_list = []
        game1 = GameList(0, 0, "Funcoaster", "Action", "Much fun", 19.90, "http://fun.io", 0, 0)
        game2 = GameList(0, 0, "Morefun", "Action", "Much fun", 19.90, "http://fun.io", 5000, 3)
        game_list.append(game1)
        game_list.append(game2)
        document = render_to_string("game_server/store.html", {'games': game_list})
        self.assertRaises(Exception, self.parser.parse(document))

class ModelFunctions(TestCase):
    """Tests custom model functions"""
    fixtures = ['test_data.json']

    def test_purchase_incrementing(self):
        """Test that purchases are incremented when new PurchasedGames object is created"""

        developer = User.objects.create_user(username="Test_Dev", password="Testing",
                                             email="Tester@email.com", first_name="first_name",
                                             last_name="last_name")
        UserType.objects.create(user_id=developer, developer=True, verification_bytes="")

        player = User.objects.create_user(username="Test_Player", password="Testing",
                                          email="Tester@email.com", first_name="first_name",
                                          last_name="last_name")

        UserType.objects.create(user_id=player, developer=False, verification_bytes="")

        game = GameList.objects.create(user_id=developer, game_name="Climbers", category="Arcade",
                                       description="AA", price=11.15, url="http://www.com")
        self.assertEqual(game.num_of_purchases, 0)

        PurchasedGames.objects.create(user_id=player, game=game)
        self.assertEqual(game.num_of_purchases, 1)

    def test_high_score(self):
        """Tests that high score gets stored when higher than previous"""
        other_player = User.objects.get(username="something")
        game = GameList.objects.get(game_name="Test Game")
        game_instance = PurchasedGames.objects.create(user_id=other_player, game=game)

        #Check that global high score matches that of database
        self.assertEqual(game.high_score, 40)

        #Add new score that is lower than global high score, should only update personal high score
        game_instance.update_score(30)
        self.assertEqual(game.high_score, 40)
        self.assertEqual(game_instance.high_score, 30)

        #Check that both global and personal high score have been updated
        game_instance.update_score(50)
        self.assertEqual(game.high_score, 50)
        self.assertEqual(game_instance.high_score, 50)

        #Also check that other player stuff is unaffected
        player = User.objects.get(username="player")

        other_game_instance = get_purchased_game_instance(player.pk, game.pk)
        self.assertEqual(other_game_instance.high_score, 40)

class AccessRights(TestCase):
    """Tests if authorization works correctly"""
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_game_playing(self):
        """Checks that only owned games can be played"""

        #Try playing a game with access rights
        self.client.force_login(User.objects.get(username="player"))
        response = self.client.get('/playgame/1')
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        #Try playing the same game without rights
        self.client.force_login(User.objects.get(username="something"))
        response = self.client.get('/playgame/1')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_game_editing(self):
        """Checks that only games added by oneself can be edited"""

        #Try editing a game that has been personally added
        self.client.force_login(User.objects.get(username="developer"))
        response = self.client.get('/editgame/1')
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        #Try editing a game added by someone else
        self.client.force_login(User.objects.get(username="other_dev"))
        response = self.client.get('/editgame/1')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_game_deleting(self):
        """Checks that only games added by oneself can be deleted"""

        #Try deleting a game that has been personally added
        self.client.force_login(User.objects.get(username="developer"))
        response = self.client.get('/deletegame/1')
        self.assertEqual(response.status_code, 302)
        self.client.logout()

        #Try deleting a game added by someone else
        self.client.force_login(User.objects.get(username="other_dev"))
        response = self.client.get('/deletegame/2')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_game_statistics(self):
        """Checks that developers can view statistics of own games only"""

        #Try viewing statistics of a game that has been personally added
        self.client.force_login(User.objects.get(username="developer"))
        response = self.client.get('/gamestats/1')
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        #Try viewing statistics of a game that has been added by someone else
        self.client.force_login(User.objects.get(username="other_dev"))
        response = self.client.get('/gamestats/1')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

class IntegrationTests(StaticLiveServerTestCase):
    """Integration tests by using the Selenium web drivers"""
    fixtures = ['test_data.json']

    def setUp(self):
        self.driver = WebDriver()

    def login_player(self):
        """Helper function for logging in as a player"""
        self.driver.get('%s%s' % (self.live_server_url, '/login'))

        username = self.driver.find_element_by_id('id_username')
        password = self.driver.find_element_by_id('id_password')
        submit = self.driver.find_element_by_tag_name('button')

        username.send_keys('player')
        password.send_keys('player')

        submit.click()

    def login_developer(self):
        """Helper function for logging in as a developer"""
        self.driver.get('%s%s' % (self.live_server_url, '/login'))

        username = self.driver.find_element_by_id('id_username')
        password = self.driver.find_element_by_id('id_password')
        submit = self.driver.find_element_by_tag_name('button')

        username.send_keys('developer')
        password.send_keys('developer')

        submit.click()

    def test_login(self):
        """Test that logging in works properly"""
        self.login_player()

        assert 'player Account' in self.driver.page_source

    def test_registration(self):
        """
        Test that registration completes, a verification email notification is sent and that
        verification works
        """
        self.driver.get('%s%s' % (self.live_server_url, '/register'))

        first_name = self.driver.find_element_by_id('id_first_name')
        last_name = self.driver.find_element_by_id('id_last_name')
        username = self.driver.find_element_by_id('id_username')
        email = self.driver.find_element_by_id('id_email')
        password1 = self.driver.find_element_by_id('id_password')
        password2 = self.driver.find_element_by_id('id_password1')
        submit = self.driver.find_element_by_tag_name('button')

        first_name.send_keys('Selenium')
        last_name.send_keys('Tester')
        username.send_keys('selenium')
        email.send_keys('selenium@tester.com')
        password1.send_keys('qwerty')
        password2.send_keys('qwerty')

        submit.click()

        #Check that the user is not active but email is supposedly sent
        test_user = User.objects.get(username="selenium")
        assert 'User successfully created, verification email sent!' in self.driver.page_source
        self.assertEqual(test_user.is_active, False)

        #Enter verification bytes and check that the user has been activated
        verification_bytes = test_user.type.verification_bytes
        self.driver.get('%s%s%s' % (self.live_server_url, '/user_verification/',
                                    verification_bytes))
        assert 'User selenium has been verified. Please login.' in self.driver.page_source
        self.assertEqual(User.objects.get(username="selenium").is_active, True)

    def test_purchasing_game(self):
        """Tests that game can be purchased"""
        self.login_player()
        self.driver.get('%s%s' % (self.live_server_url, '/gamestorepage/3'))

        buy_button = self.driver.find_element_by_xpath("//input[@type='submit']")
        buy_button.click()

        confirm_button = self.driver.find_element_by_xpath("//button[text()='Pay']")
        confirm_button.click()

        assert 'has now been added to your game list!' in self.driver.page_source

    def test_editing_game(self):
        """Tests that game details can be edited by navigating through my games"""
        self.login_developer()
        self.driver.get('%s%s' % (self.live_server_url, '/mygames'))

        game_entry = self.driver.find_element_by_class_name('game-list-container')
        game_entry.click()

        edit_button = self.driver.find_element_by_link_text('Edit')
        edit_button.click()

        modify_button = self.driver.find_element_by_xpath("//button[text()='Modify']")
        game_name = self.driver.find_element_by_id('id_game_name')
        game_name.clear()
        game_name.send_keys('New game name')

        modify_button.click()

        assert 'New game name details have been updated.' in self.driver.page_source

    def test_playing_game(self):
        """Test playing, acquiring score, submitting the score and that score is saved"""
        self.login_player()
        self.driver.get('%s%s' % (self.live_server_url, '/boughtgames'))

        game_entry = self.driver.find_elements_by_class_name('game-list-container')[1]
        game_entry.click()

        play_button = self.driver.find_elements_by_link_text('Play')[1]
        play_button.click()

        assert 'Test Game' in self.driver.page_source

        self.driver.switch_to.frame(self.driver.find_element_by_id('gameFrame'))
        add_score_button = self.driver.find_element_by_id('add_points')

        #Click the button 5 times totaling 50 score
        add_score_button.click()
        add_score_button.click()
        add_score_button.click()
        add_score_button.click()
        add_score_button.click()

        submit_score_button = self.driver.find_element_by_id('submit_score')
        submit_score_button.click()

        self.driver.get('%s%s' % (self.live_server_url, '/boughtgames'))
        game_entry = self.driver.find_elements_by_class_name('game-list-container')[1]
        game_entry.click()

        game_table = self.driver.find_element_by_xpath(
            '(//table[@class="game-list-stats"])[2]//tr[2]')
        self.assertEqual(game_table.text, 'Personal highscore: 50')

    def tearDown(self):
        self.driver.quit()
