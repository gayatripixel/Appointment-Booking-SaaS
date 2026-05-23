from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.services.models import Service
from apps.shops.models import Shop
from apps.staff.models import Staff


class Booking(models.Model):
    """Model representing a customer booking/appointment."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        NO_SHOW = 'no_show', 'No Show'

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
    )
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='bookings',
    )

    # Booking date and time
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # Guest booking info (for non-registered users)
    guest_name = models.CharField(max_length=100, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)

    # Additional info
    notes = models.TextField(blank=True, help_text='Customer notes or special requests')
    cancellation_reason = models.TextField(blank=True)

    # Price at time of booking (in case service price changes later)
    price = models.DecimalField(max_digits=10, decimal_places=2)


    # Payment info
    payment_status = models.CharField(
       max_length=20,
       default='pending'
    )

    stripe_payment_intent = models.CharField(
      max_length=255,
      blank=True,
      null=True
    )

    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        customer_name = self.customer_display_name
        return f'{customer_name} - {self.service.name} on {self.date} at {self.start_time}'

    @property
    def customer_display_name(self):
        """Return customer name whether registered or guest."""
        if self.customer:
            return self.customer.get_full_name() or self.customer.email
        return self.guest_name or 'Guest'

    @property
    def customer_email(self):
        """Return customer email whether registered or guest."""
        if self.customer:
            return self.customer.email
        return self.guest_email

    @property
    def customer_phone(self):
        """Return customer phone whether registered or guest."""
        if self.customer:
            return self.customer.phone
        return self.guest_phone

    @property
    def is_past(self):
        """Check if booking is in the past."""
        from datetime import datetime
        booking_datetime = datetime.combine(self.date, self.end_time)
        return timezone.make_aware(booking_datetime) < timezone.now()

    @property
    def is_upcoming(self):
        """Check if booking is upcoming and active."""
        return not self.is_past and self.status in [self.Status.PENDING, self.Status.CONFIRMED]

    @property
    def can_cancel(self):
        """Check if booking can be cancelled."""
        return self.is_upcoming and self.status not in [self.Status.CANCELLED, self.Status.COMPLETED]

    def confirm(self):
        """Confirm the booking."""
        if self.status == self.Status.PENDING:
            self.status = self.Status.CONFIRMED
            self.save(update_fields=['status', 'updated_at'])

    def cancel(self, reason=''):
        """Cancel the booking."""
        if self.can_cancel:
            self.status = self.Status.CANCELLED
            self.cancellation_reason = reason
            self.save(update_fields=['status', 'cancellation_reason', 'updated_at'])

    def complete(self):
        """Mark booking as completed."""
        if self.status in [self.Status.PENDING, self.Status.CONFIRMED]:
            self.status = self.Status.COMPLETED
            self.save(update_fields=['status', 'updated_at'])

    def mark_no_show(self):
        """Mark booking as no-show."""
        if self.status in [self.Status.PENDING, self.Status.CONFIRMED]:
            self.status = self.Status.NO_SHOW
            self.save(update_fields=['status', 'updated_at'])
