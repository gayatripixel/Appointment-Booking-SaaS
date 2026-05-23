import logging

import resend
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via Resend API."""

    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY

    def send_email(self, to_email, subject, html_content, from_email=None):
        """Send an email using Resend API."""
        if not settings.RESEND_API_KEY:
            logger.warning('RESEND_API_KEY not configured, skipping email send')
            return False

        try:
            params = {
                'from': from_email or settings.DEFAULT_FROM_EMAIL,
                'to': [to_email],
                'subject': subject,
                'html': html_content,
            }
            resend.Emails.send(params)
            logger.info(f'Email sent successfully to {to_email}')
            return True
        except Exception as e:
            logger.error(f'Failed to send email to {to_email}: {str(e)}')
            return False

    def send_verification_email(self, user, token, request=None):
        """Send email verification link to user."""
        verification_url = reverse('accounts:verify_email', kwargs={'token': token})

        if request:
            verification_url = request.build_absolute_uri(verification_url)
        else:
            verification_url = f'{settings.SITE_URL}{verification_url}'

        html_content = render_to_string('emails/verification.html', {
            'user': user,
            'verification_url': verification_url,
        })

        return self.send_email(
            to_email=user.email,
            subject='Verify your AppointHub account',
            html_content=html_content,
        )

    def send_account_exists_email(self, email, request=None):
        """Send email notifying user that account already exists (for failed registration)."""
        login_url = reverse('accounts:login')
        reset_url = reverse('accounts:password_reset_request')

        if request:
            login_url = request.build_absolute_uri(login_url)
            reset_url = request.build_absolute_uri(reset_url)
        else:
            login_url = f'{settings.SITE_URL}{login_url}'
            reset_url = f'{settings.SITE_URL}{reset_url}'

        html_content = render_to_string('emails/account_exists.html', {
            'email': email,
            'login_url': login_url,
            'reset_url': reset_url,
        })

        return self.send_email(
            to_email=email,
            subject='AppointHub Registration Attempt',
            html_content=html_content,
        )

    def send_password_reset_email(self, user, token, request=None):
        """Send password reset link to user."""
        reset_url = reverse('accounts:password_reset_confirm', kwargs={'token': token})

        if request:
            reset_url = request.build_absolute_uri(reset_url)
        else:
            reset_url = f'{settings.SITE_URL}{reset_url}'

        html_content = render_to_string('emails/password_reset.html', {
            'user': user,
            'reset_url': reset_url,
        })

        return self.send_email(
            to_email=user.email,
            subject='Reset your AppointHub password',
            html_content=html_content,
        )

    def send_booking_confirmation(self, booking):
        """Send booking confirmation email to customer."""
        html_content = render_to_string('emails/booking_confirmation.html', {
            'booking': booking,
        })

        return self.send_email(
            to_email=booking.customer.email,
            subject=f'Booking Confirmed - {booking.service.name}',
            html_content=html_content,
        )

    def send_booking_reminder(self, booking):
        """Send booking reminder email to customer (24 hours before)."""
        html_content = render_to_string('emails/booking_reminder.html', {
            'booking': booking,
        })

        return self.send_email(
            to_email=booking.customer.email,
            subject=f'Reminder: Your appointment tomorrow - {booking.service.name}',
            html_content=html_content,
        )

    def send_booking_cancellation(self, booking, cancelled_by='customer'):
        """Send booking cancellation notice."""
        html_content = render_to_string('emails/booking_cancellation.html', {
            'booking': booking,
            'cancelled_by': cancelled_by,
        })

        return self.send_email(
            to_email=booking.customer.email,
            subject=f'Booking Cancelled - {booking.service.name}',
            html_content=html_content,
        )


# Singleton instance
email_service = EmailService()
