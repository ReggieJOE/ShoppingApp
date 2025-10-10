from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'payment_method']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 4}),
            'payment_method': forms.Select(choices=[
                ('credit_card', 'Credit Card'),
                ('debit_card', 'Debit Card'),
                ('paypal', 'PayPal'),
                ('cash_on_delivery', 'Cash on Delivery'),
            ])
        }