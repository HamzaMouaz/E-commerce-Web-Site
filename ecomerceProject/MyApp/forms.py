from django import forms

#from chatbotApp.models import CustomUser
from django.contrib.auth.forms import UserCreationForm

from MyApp.models import Produit, ShippingInformation, Userr

class SignUpForm(UserCreationForm):
    class Meta:
        model = Userr
        fields = ('username', 'password1', 'password2')

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['image', 'name', 'old_price', 'price']

class ShippingInformationForm(forms.ModelForm):
    class Meta:
        model = ShippingInformation
        fields = ['full_name', 'phone_number', 'wilaya', 'city', 'address']
