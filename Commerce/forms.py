from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(
        label="Shipping Address",
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'House Number & Street, Area, City, Region, Ghana Postal Code'
        }),
        required=True
    )

    payment_method = forms.ChoiceField(
        label="Payment Method",
        choices=[
            ('', 'Select a payment method'),
            ('mobile_money', 'Mobile Money'),
            ('credit_card', 'Credit Card'),
            ('debit_card', 'Debit Card'),
            ('cash_on_delivery', 'Cash on Delivery'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        required=True
    )

    card_number = forms.CharField(
        label="Card Number",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'maxlength': 19
        })
    )

    card_expiry = forms.CharField(
        label="Expiry Date",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'maxlength': 5
        })
    )

    card_cvv = forms.CharField(
        label="CVV",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123',
            'maxlength': 4
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        card_number = cleaned_data.get('card_number')
        card_expiry = cleaned_data.get('card_expiry')
        card_cvv = cleaned_data.get('card_cvv')

        # Validate card details only if credit/debit card is selected
        if payment_method in ['credit_card', 'debit_card']:
            if not card_number:
                raise forms.ValidationError("Card number is required for card payments.")
            if not card_expiry:
                raise forms.ValidationError("Expiry date is required for card payments.")
            if not card_cvv:
                raise forms.ValidationError("CVV is required for card payments.")

        return cleaned_data