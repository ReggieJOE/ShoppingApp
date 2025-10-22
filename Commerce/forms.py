from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from unicodedata import category

from .models import Product

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password',
            'id': 'password1'
        })
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'id': 'password2'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        # Remove default help text
        self.fields['password1'].help_text = None
        self.fields['username'].help_text = None


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
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'category','image','calories']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step':'0.01'}),
        }