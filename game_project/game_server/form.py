from django import forms
from django.contrib.auth.models import User
from game_server.models import GameList

class UserForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=64, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(label='Last Name', max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    username = forms.CharField(min_length=6, label='Username', max_length=32, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(label='Email', max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(min_length=6, max_length=32, label='Password', widget=forms.PasswordInput)
    password1 = forms.CharField(min_length=6, max_length=32, label='Password confirmation', widget=forms.PasswordInput)
    user_type = forms.BooleanField(label='Check If Developer', required=False)
    class Meta:
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'password1']
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        password1 = cleaned_data.get("password1")
        if password != password1:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )
    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('Duplicate User Exists')

class UserPasswordResetForm(forms.Form):
    password = forms.CharField(min_length=6, max_length=32, label='Password', widget=forms.PasswordInput)
    password1 = forms.CharField(min_length=6, max_length=32, label='Password confirmation', widget=forms.PasswordInput)
    class Meta:
        fields = ['password', 'password1']
    def clean(self):
        cleaned_data = super(UserPasswordResetForm, self).clean()
        password = cleaned_data.get("password")
        password1 = cleaned_data.get("password1")
        if password != password1:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )


class UserEditForm(forms.ModelForm):
    first_name = forms.CharField(label='First Name', max_length=64, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(label='Last Name', max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class LoginForm(forms.Form):
    username = forms.CharField(min_length=6, label='Username', max_length=32, widget=forms.TextInput(attrs={'class': 'form-control input-lg', 'name': 'username', 'placeholder': 'Username'}))
    password = forms.CharField(min_length=6, max_length=32, label='Password', widget=forms.PasswordInput)
    class Meta:
        fields = ['username','password']



class GameListForm(forms.ModelForm):
    game_name = forms.CharField(label='Name of Game', max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Game Title'}))
    category = forms.ChoiceField(choices=[('Action', 'Action'), ('Arcade', 'Arcade'), ('Adventure','Adventure'),
                                          ('Multiplayer', 'Multiplayer'), ('Sports', 'Sports'), ('Racing','Racing'),
                                          ('Fight', 'Fight'), ('Strategy', 'Strategy'), ('Minigame', 'Minigame'),
                                          ('Puzzle', 'Puzzle'), ('Educational', 'Educational')], required=True)
    description = forms.CharField(min_length=6, label='Description', widget=forms.Textarea(attrs={'placeholder': 'Description of Game'}))
    price = forms.DecimalField(max_digits=6, decimal_places=2, required=True)
    image = forms.ImageField()
    url = forms.CharField(min_length=6, max_length=512, label='Game Link', widget=forms.TextInput(attrs={'placeholder': 'Link of Game'}))
    class Meta:
        model = GameList
        fields = ['game_name', 'category', 'description', 'price', 'image', 'url']
