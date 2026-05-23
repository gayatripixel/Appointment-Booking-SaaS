from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import SetPasswordForm

from .models import User


class RegistrationForm(forms.ModelForm):
    """Form for user registration."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        min_length=8,
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        label='Confirm Password',
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Email address'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone number (optional)'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        # Don't reveal whether email exists - handle in view
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Passwords do not match.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_active = False  # Require email verification
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Form for user login."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email address'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
    )

    def __init__(self, *args, **kwargs):
     self.request = kwargs.pop('request', None)   # ⭐ IMPORTANT
     self.user = None
     super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            email = email.lower()
            self.user = authenticate(
             request=self.request,
             email=email,
             password=password
            )

            if self.user is None:
                raise forms.ValidationError('Invalid email or password.')

            if not self.user.is_active:
                raise forms.ValidationError(
                    'Your account is not active. Please verify your email.'
                )

        return cleaned_data

    def get_user(self):
        return self.user


class PasswordResetRequestForm(forms.Form):
    """Form for requesting a password reset."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email address'}),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        # Don't reveal whether the email exists
        return email


class PasswordResetForm(SetPasswordForm):
    """Form for setting a new password after reset."""
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New password'}),
        label='New Password',
        min_length=8,
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}),
        label='Confirm New Password',
    )


class ProfileForm(forms.ModelForm):
    """Form for updating user profile."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone number'}),
        }
