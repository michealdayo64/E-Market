from django import forms
from django.contrib.auth.models import User
from eMarket.models import UserInfo

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'password', 'email')

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ('phone_no', 'address')

PAYMENT_CHOICES = (
    ('S', 'STRIPE'),
    ('P', 'PAYPAL')
)

class CheckoutForm(forms.Form):
    first_name = forms.CharField(widget = forms.TextInput(attrs = {
        'placeholder' : 'Enter First Name'
    }))
    last_name = forms.CharField(widget = forms.TextInput(attrs = {
        'placeholder' : 'Enter Last Name'
    }))
    country = forms.CharField(widget = forms.TextInput(attrs = {
        'placeholder' : 'Enter country'
    }))
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder' : '1234 Main St'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder' : 'Apartment or suite'
    }))
    city = forms.CharField(widget = forms.TextInput(attrs = {
        'placeholder' : 'Enter city'
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class' : 'form-control'
    }))
    order_note = forms.CharField(widget = forms.TextInput(attrs = {
        'placeholder': 'Note about your order, e.g special note for delivery'
    }))
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)