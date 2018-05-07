"""Includes all views that produce HTML output and other functionality crucial views"""

import random
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.crypto import get_random_string
from game_server.form import UserForm, GameListForm, UserPasswordResetForm, UserEditForm
from game_server.models import GameList, PurchasedGames, UserType
from game_server.helperfunctions import user_owns_game, create_checksum, usertype_exists

#Unique key for payment. Seller ID == karhuserver
#Secret Key created by Payment Module == 272491baabdac31e5f7ca278941c9f95
SID = 'karhuserver'
SECRET_KEY = '272491baabdac31e5f7ca278941c9f95'

def home(request):
    """
    The main home page which displays the newest games added to the service
    """
    latest_games = GameList.objects.filter(active=True).order_by("-time_added")[:4]
    return render(request, "game_server/home.html", {'latest_games': latest_games})

def store(request):
    """
    Main store view which lists all games available in the store and provides search and sorting
    functionalities
    """

    ordering = ""
    game_list = None

    #Check first if any games have been added to the store yet
    if not GameList.objects.all().filter(active=True):
        store_empty = True
    else:
        store_empty = False

        if request.GET.get("search"):
            game_list = GameList.objects.filter(game_name__icontains=request.GET.get("search"),
                                                active=True)
        elif request.GET.get("order"):
            order = request.GET.get("order")
            if order == "title":
                ordering = "game_name"
            elif order == "genre":
                ordering = "category"
            elif order == "popularity":
                ordering = "-num_of_purchases"
            elif order == "release":
                ordering = "-time_added"
            elif order == "price":
                ordering = "price"
            if ordering:
                game_list = GameList.objects.order_by(ordering).filter(active=True)
            else:
                game_list = GameList.objects.all().filter(active=True)
        else:
            game_list = GameList.objects.all().filter(active=True)

    return render(request, "game_server/store.html",
                  {'games': game_list, 'store_empty': store_empty})

def gamestorepage(request, gameid):
    """
    The store page which displays product information for a specific product. This page also allows
    initing purchases if the user is a non-developer and doesn't own the game yet.
    """
    if request.user.is_authenticated and not usertype_exists(request.user):
        return redirect('social_registration')

    game = get_object_or_404(GameList, pk=gameid, active=True)

    #Recommend games based on the same genre/category, excluding the current game
    recommended_games = GameList.objects.filter(
        category=game.category, active=True).exclude(pk=gameid)

    if len(recommended_games) > 3:
        #This is does a random slice only since order_by('?') is very expensive
        start_index = int(random.random() * (len(recommended_games) - 3))
        recommended_games = recommended_games[start_index:start_index+3]

    if request.user.is_authenticated() and not request.user.type.developer:

        #Owned attribute is used by the template to determine if buy button should be shown
        owned = user_owns_game(request.user, gameid)

        # redirect user to home if user does not own the game and game is deactivated
        if not game.active and not owned:
            return redirect('home')

        #Payment Commands

        #Product ID concatenated with user id to prevent the same checksum (purchase link) from
        #being used by other users
        pid = '%s_%s' % (gameid, request.user.pk)
        checksum = create_checksum("pid={}&sid={}&amount={}&token={}",
                                   pid, SID, game.price, SECRET_KEY)
        return render(request, "game_server/gamestorepage.html",
                      {'game': game, 'author': GameList.objects.get(pk=gameid).user_id,
                       'owned': owned, 'pid': pid, 'sid': SID, 'checksum': checksum,
                       'recommended_games': recommended_games})
    return render(request, "game_server/gamestorepage.html",
                  {'game': game, 'author': GameList.objects.get(pk=gameid).user_id,
                   'recommended_games': recommended_games})

@login_required
@user_passes_test(usertype_exists, login_url='/social_registration', redirect_field_name=None)
def mygames(request):
    """
    Developer view
    Shows all games uploaded by the current user
    """
    if request.user.type.developer:
        return render(request, "game_server/mygames.html",
                      {'games': GameList.objects.filter(user_id=request.user)})
    return HttpResponseForbidden()


@login_required
@user_passes_test(usertype_exists, login_url='/social_registration', redirect_field_name=None)
def boughtgames(request):
    """
    Player view
    Shows all games bought by the current user
    """
    if not request.user.type.developer:
        purchased_games = PurchasedGames.objects.select_related().filter(user_id=request.user)
        return render(request, "game_server/boughtgames.html",
                      {'purchased_games': purchased_games})
    return HttpResponseForbidden()


@login_required
@user_passes_test(usertype_exists, login_url='/social_registration', redirect_field_name=None)
def playgame(request, gameid):
    """
    Player view
    Used to play game with gameid if the title has been purchased
    """
    if user_owns_game(request.user, gameid):
        return render(request, "game_server/playgame.html",
                      {'game': GameList.objects.get(pk=gameid)})
    return HttpResponseForbidden()


@login_required
@user_passes_test(usertype_exists, login_url='/social_registration', redirect_field_name=None)
def buygame(request):
    """
    Player view
    Return view from payment service which verifies the payment info and adds the game if the
    information has not been tampered with
    """
    if request.user.type.developer:
        return HttpResponseForbidden()

    pid = request.GET.get('pid')
    ref = request.GET.get('ref')
    result = request.GET.get('result')
    checksum = request.GET.get('checksum')
    checksum_new = create_checksum("pid={}&ref={}&result={}&token={}", pid, ref, result, SECRET_KEY)

    pid_data = pid.split('_')

    gameid = int(pid_data[0])
    userid = int(pid_data[1])

    try:
        game = GameList.objects.get(pk=gameid)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest()

    if user_owns_game(request.user, gameid):
        return redirect('home')

    if checksum == checksum_new and request.user.pk == userid:
        if result == 'success':
            PurchasedGames.objects.create(user_id=request.user, game=game)
            messages.success(request, '%s has now been added to your game list!' % (game.game_name))
            return redirect('boughtgames')
        elif result == 'cancel':
            messages.warning(request, 'Payment unsuccessful. You have canceled the payment.')
            return redirect('boughtgames')
    messages.error(request, 'An error occured while processing your purchase.')
    return redirect('home')

def register(request):
    """
    Displays the user registration form and creates a new user based on the data,
    sending a verification email
    """
    if not request.user.is_authenticated:
        form = UserForm()
        if request.method == 'POST':
            form = UserForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                email = form.cleaned_data['email']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                user_type = form.cleaned_data['user_type']
                user = User.objects.create_user(username=username, password=password, email=email,
                                                first_name=first_name, last_name=last_name,
                                                is_active=False)
                verification_code = get_random_string(length=64)
                save_type = UserType(user_id=user, developer=user_type,
                                     verification_bytes=verification_code)
                user.save()
                save_type.save()

                email = EmailMessage('Karhu Game Server User Verification',
                                     ("Kindly click the link below to verify your email address:\n"
                                      "http://%s/user_verification/%s/" % (request.get_host(),
                                                                           verification_code)),
                                     to=[email])
                email.send()
                messages.info(request, 'User successfully created, verification email sent!')
                return redirect('login')
        return render(request, "game_server/register.html", {'form': form})
    else:
        return redirect('home')

def verification_email(request, verification_bytes):
    """
    View used to activate users following registration if matching verification bytes are found
    Example URL: http://127.0.0.1/user_verification/dsajkbh78w43rhfdnhgo9wthfrsahg
    """
    try:
        user_identity = UserType.objects.get(verification_bytes=verification_bytes).user_id
        UserType.objects.filter(
            verification_bytes=verification_bytes).update(verification_bytes='.')
        User.objects.filter(username=user_identity).update(is_active=True)
        messages.success(request, 'User '+str(user_identity)+' has been verified. Please login.')
    except ObjectDoesNotExist:
        messages.error(request, 'User not found in database or the verification code is incorrect '
                       'or already used.')
    return render(request, "game_server/home.html")

@login_required
@user_passes_test(usertype_exists, login_url='/social_registration', redirect_field_name=None)
def addgames(request):
    """
    Developer view
    Displays the form for adding new games to the service
    """
    if request.user.type.developer:
        form = GameListForm()
        if request.method == 'POST':
            form = GameListForm(request.POST, request.FILES)
            form.user_id_id = request.user
            form.high_score = 0
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user_id = request.user
                instance.high_score = 0
                instance.active = True
                instance.save()
                messages.success(request, str(instance.game_name) +
                                 ' has been added to the game store.')
                return redirect('mygames')
        return render(request, "game_server/addgames.html", {'form': form})
    else:
        return redirect('home')

@login_required
@user_passes_test(usertype_exists, login_url='/social_registration', redirect_field_name=None)
def editgame(request, game_id):
    """
    Developer view
    Disiplays the form for editing a game added by oneself
    """
    try:
        if request.user == GameList.objects.get(pk=game_id).user_id:
            instance = GameList.objects.get(id=game_id)
            form = GameListForm(request.POST or None, request.FILES or None, instance=instance)
            if request.method == 'POST':
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.user_id = request.user
                    instance.save()
                    messages.info(request, str(instance.game_name) + ' details have been updated.')
                    return redirect('mygames')
            return render(request, "game_server/editgame.html", {'form': form})
        else:
            return HttpResponseForbidden()
    except ObjectDoesNotExist:
        return HttpResponseBadRequest()

@login_required
@user_passes_test(usertype_exists, login_url='/social_registration', redirect_field_name=None)
def deletegame(request, game_id):
    """
    Developer view
    Used for deleting a game added by oneself
    """
    try:
        game_entry = GameList.objects.get(pk=game_id)
        if request.user == game_entry.user_id:
            if game_entry.num_of_purchases == 0:
                messages.info(request, str(game_entry.game_name) + ' has been deleted.')
                game_entry.image.delete(save=True)
                game_entry.delete()
            elif game_entry.active:
                game_entry.active = False
                game_entry.save()
                messages.warning(request, '%s has been deactived and not deleted because the game '
                                 'has been purchased %d time(s).'
                                 % (game_entry.game_name, game_entry.num_of_purchases))
            else:
                messages.error(request, '%s cannot be deleted because it has been purchased %d '
                               'time(s).'
                               % (game_entry.game_name, game_entry.num_of_purchases))
            return redirect('mygames')
        return HttpResponseForbidden()
    except ObjectDoesNotExist:
        return HttpResponseBadRequest()


@login_required
@user_passes_test(usertype_exists, login_url='/social_registration', redirect_field_name=None)
def activategame(request, game_id):
    """
    Developer view
    Used for activating a game that has been deactivated
    """
    try:
        game_entry = GameList.objects.get(pk=game_id, active=False)
        if request.user == game_entry.user_id:
            game_entry.active = True
            game_entry.save()
            messages.info(request, '%s has been reactivated and can now be purchased from the game '
                          'store.' % (game_entry.game_name))
            return redirect('mygames')
        return HttpResponseForbidden()
    except ObjectDoesNotExist:
        return HttpResponseBadRequest()

@login_required
@user_passes_test(usertype_exists, login_url='/social_registration', redirect_field_name=None)
def deactivategame(request, game_id):
    """
    Developer view
    Used for deactivating a game that is active
    """
    try:
        game_entry = GameList.objects.get(pk=game_id, active=True)
        if request.user == game_entry.user_id:
            game_entry.active = False
            game_entry.save()
            messages.info(request, '%s has been deactivated and removed from the game store.'
                          % (game_entry.game_name))
            return redirect('mygames')
        return HttpResponseForbidden()
    except ObjectDoesNotExist:
        return HttpResponseBadRequest()

@login_required
@user_passes_test(usertype_exists, login_url='/social_registration', redirect_field_name=None)
def gamestats(request, game_id):
    """
    Developer view
    Used for seeing timeline of game stats (when game was added and when it has been purchased)
    """
    game = get_object_or_404(GameList, pk=game_id)
    if request.user.type.developer and request.user == game.user_id:
        purchases = PurchasedGames.objects.filter(game_id=game_id).order_by('purchase_time')
        return render(request, "game_server/gamestats.html",
                      {'game': game, 'game_purchases': purchases})
    return HttpResponseForbidden()

def logout(request):
    """
    View used for logging out of the service
    """
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('home')

def login(request):
    """
    View used for logging in to the service
    """
    if not request.user.is_authenticated:
        form = AuthenticationForm()
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=raw_password)
                auth_login(request, user)
                return redirect('home')
        return render(request, "game_server/login.html", {'form': form})
    else:
        return redirect('home')

def resetpassword(request):
    """
    View used for requesting a password reset email
    """
    if request.method == 'POST':
        username = request.POST['username']
        try:
            user = User.objects.get(username=username)
            if user.is_active:
                verification_code = get_random_string(length=64)
                email = EmailMessage('Karhu Game Server Password Reset',
                                     ("Kindly click the link below to reset your password:\n"
                                      "http://%s/reset_password/%s/" % (request.get_host(),
                                                                        verification_code)),
                                     to=[str(user.email)])
                UserType.objects.filter(pk=user.id).update(verification_bytes=verification_code)
                email.send()
                messages.info(request, 'Password reset email has been sent to your registered '
                              'email address at ' + str(user.email))
            else:
                messages.warning(request, 'Account is not active. Please activate your account '
                                 'before attemping to reset its password.')
        except ObjectDoesNotExist:
            messages.error(request, 'No user exists with this username')
    return render(request, "game_server/forgotpassword.html")

def reset_password(request, verification_bytes):
    """
    View used to verify password reset request and to specify a new password if matching
    verification bytes are found
    Example URL: http://127.0.0.1/reset_password/dsajkbh78w43rhfdnhgo9wthfrsahg
    """
    form = UserPasswordResetForm()
    try:
        user_identity = UserType.objects.get(verification_bytes=verification_bytes).user_id
        if request.method == 'POST':
            form = UserPasswordResetForm(data=request.POST)
            if form.is_valid():
                user = User.objects.get(pk=user_identity.pk)
                user.set_password(form.cleaned_data.get('password'))
                user.save()
                UserType.objects.filter(
                    verification_bytes=verification_bytes).update(verification_bytes='.')
                messages.success(request, 'Password changed successfully. Please login')
                return render(request, "game_server/home.html")

            return render(request, "game_server/reset_password.html", {'form': form})
        return render(request, "game_server/reset_password.html", {'form': form})
    except ObjectDoesNotExist:
        messages.error(request, 'User not found in database or the verification code is incorrect '
                       'or already used.')
    return render(request, "game_server/home.html")

@login_required
def accountdetails(request):
    """
    Used for changing account details such as first name, last name and password
    """
    if request.user.email:
        user = User.objects.get(pk=request.user.id)
        form1 = UserEditForm(instance=user)
        form2 = UserPasswordResetForm()
        if request.method == 'POST':
            action = request.POST['action']
            if action == 'update':
                form1 = UserEditForm(request.POST or None, instance=user)
                if form1.is_valid():
                    user.first_name = form1.cleaned_data.get('first_name')
                    user.last_name = form1.cleaned_data.get('last_name')
                    user.save()
                    messages.success(request, 'User details updated')
                    return render(request, "game_server/home.html")
            else:
                form2 = UserPasswordResetForm(request.POST or None)
                if form2.is_valid():
                    user = authenticate(username=request.user.username,
                                        password=request.POST['old_password'])
                    if user:
                        user.set_password(form2.cleaned_data.get('password'))
                        user.save()
                        messages.success(request, 'Password changed successfully.')
                        return render(request, "game_server/home.html")
                    else:
                        messages.error(request, 'Old password incorrect.')
        return render(request, "game_server/account.html", {'form1': form1, 'form2': form2})
    return redirect('home')

@login_required
def social_registration(request):
    """
    Used for specifying if the user is a developer or a player when logging in via a
    3rd party service
    """
    try:
        if request.user.type:
            return redirect('home')
    except ObjectDoesNotExist:
        if request.POST:
            type_of_user = request.POST['type_of_user']
            save_type = UserType(user_id=request.user, developer=type_of_user)
            save_type.save()
            return redirect('home')
    return render(request, "game_server/social_register.html")
