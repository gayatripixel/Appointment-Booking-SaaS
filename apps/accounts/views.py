import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django_ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)

from .forms import (
    LoginForm,
    PasswordResetForm,
    PasswordResetRequestForm,
    ProfileForm,
    RegistrationForm,
)
from .models import EmailVerificationToken, PasswordResetToken, User
from apps.notifications.services import email_service


from django.conf import settings

def landing_view(request):
    context = {
        "razorpay_key": getattr(settings, "RAZORPAY_KEY_ID", None)
    }
    return render(request, "landing.html", context)

@ratelimit(key='ip', rate='10/h', method='POST', block=True)
def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if user already exists (don't reveal this to the user)
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                # Send "account exists" email instead of revealing the error
                try:
                    email_service.send_account_exists_email(email, request)
                except Exception:
                    pass  # Silently fail - don't reveal anything
            else:
                # Create new user
                user = form.save()

                # Try to send verification email
                try:
                    token = secrets.token_urlsafe(32)
                    EmailVerificationToken.objects.create(
                        user=user,
                        token=token,
                        expires_at=timezone.now() + timedelta(hours=24),
                    )

                    email_sent = email_service.send_verification_email(user, token, request)

                    if not email_sent:
                        # Email not sent (no API key), auto-verify and activate user
                        user.is_email_verified = True
                        user.is_active = True
                        user.save()
                except Exception:
                    # If email fails, auto-verify and activate
                    user.is_email_verified = True
                    user.is_active = True
                    user.save()

            # Always show the same message (don't reveal if account exists)
            messages.success(
                request,
                'Registration successful! Please check your email to verify your account.'
            )
            return redirect('accounts:login')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Handle "Remember Me" checkbox
            if not request.POST.get('remember'):
                # Session expires when browser closes
                request.session.set_expiry(0)
            # Otherwise use default SESSION_COOKIE_AGE (7 days)

            messages.success(request, f'Welcome back, {user.get_short_name()}!')

            # Redirect to next page if specified and safe
            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('dashboard:index')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


def verify_email_view(request, token):
    """Handle email verification."""
    verification_token = get_object_or_404(
        EmailVerificationToken,
        token=token,
        is_used=False,
    )

    if verification_token.is_expired:
        messages.error(request, 'This verification link has expired.')
        return redirect('accounts:login')

    # Activate user
    user = verification_token.user
    user.is_active = True
    user.is_email_verified = True
    user.save()

    # Mark token as used
    verification_token.is_used = True
    verification_token.save()

    messages.success(request, 'Email verified successfully! You can now log in.')
    return redirect('accounts:login')


@ratelimit(key='ip', rate='5/h', method='POST', block=True)
def password_reset_request_view(request):
    """Handle password reset request."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = User.objects.get(email=email)

                # Create reset token
                token = secrets.token_urlsafe(32)
                PasswordResetToken.objects.create(
                    user=user,
                    token=token,
                    expires_at=timezone.now() + timedelta(hours=1),
                )

                # Send reset email via Resend
                email_service.send_password_reset_email(user, token, request)
            except User.DoesNotExist:
                pass  # Don't reveal whether email exists

            messages.info(
                request,
                'If an account exists with this email, you will receive a password reset link.'
            )
            return redirect('accounts:login')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset_confirm_view(request, token):
    """Handle password reset confirmation."""
    reset_token = get_object_or_404(
        PasswordResetToken,
        token=token,
        is_used=False,
    )

    if reset_token.is_expired:
        messages.error(request, 'This password reset link has expired.')
        return redirect('accounts:password_reset_request')

    if request.method == 'POST':
        form = PasswordResetForm(reset_token.user, request.POST)
        if form.is_valid():
            form.save()

            # Mark token as used
            reset_token.is_used = True
            reset_token.save()

            messages.success(request, 'Password reset successful! You can now log in.')
            return redirect('accounts:login')
    else:
        form = PasswordResetForm(reset_token.user)

    return render(request, 'accounts/password_reset_confirm.html', {'form': form})


@login_required
def profile_view(request):
    """Display and update user profile."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def settings_view(request):
    """Display and update user settings."""
    user = request.user
    
    if request.method == 'POST':
        # Handle different settings sections
        section = request.POST.get('section', 'notifications')
        
        if section == 'notifications':
            user.email_notifications = request.POST.get('email_notifications') == 'on'
            user.sms_notifications = request.POST.get('sms_notifications') == 'on'
            user.booking_reminders = request.POST.get('booking_reminders') == 'on'
            user.marketing_emails = request.POST.get('marketing_emails') == 'on'
            user.save()
            messages.success(request, 'Notification settings updated!')
        
        elif section == 'privacy':
            user.profile_visible = request.POST.get('profile_visible') == 'on'
            user.show_online_status = request.POST.get('show_online_status') == 'on'
            user.save()
            messages.success(request, 'Privacy settings updated!')
        
        elif section == 'password':
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            else:
                try:
                    validate_password(new_password, user)
                    user.set_password(new_password)
                    user.save()
                    login(request, user)  # Re-login after password change
                    messages.success(request, 'Password changed successfully!')
                except ValidationError as e:
                    for error in e.messages:
                        messages.error(request, error)
        
        return redirect('accounts:settings')
    
    # Default settings values (in case fields don't exist on model yet)
    context = {
        'email_notifications': getattr(user, 'email_notifications', True),
        'sms_notifications': getattr(user, 'sms_notifications', False),
        'booking_reminders': getattr(user, 'booking_reminders', True),
        'marketing_emails': getattr(user, 'marketing_emails', False),
        'profile_visible': getattr(user, 'profile_visible', True),
        'show_online_status': getattr(user, 'show_online_status', True),
    }
    
    return render(request, 'accounts/settings.html', context)
