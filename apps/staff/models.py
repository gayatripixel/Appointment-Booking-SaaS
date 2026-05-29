from django.conf import settings
from django.db import models

from apps.services.models import Service
from apps.shops.models import Shop


class Staff(models.Model):
    """Model representing a staff member of a shop."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profiles',
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='staff_members',
    )
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='staff/photos/', blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True)

    phone = models.CharField(
     max_length=20,
     blank=True
    )

    experience = models.IntegerField(
      default=0
    )

    rating = models.FloatField(
      default=0
    )

    # Services this staff member can perform
    services = models.ManyToManyField(
        Service,
        through='StaffService',
        related_name='staff_members',
    )

    is_active = models.BooleanField(default=True)
    accepts_bookings = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Staff members'
        unique_together = ['user', 'shop']

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.shop.name})'

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.email


class StaffService(models.Model):
    """Through model for staff-service relationship with custom pricing."""

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='staff_services',
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='service_staff',
    )
    # Optional custom price/duration for this staff member
    custom_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Leave blank to use service default price',
    )
    custom_duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Leave blank to use service default duration',
    )

    class Meta:
        unique_together = ['staff', 'service']

    def __str__(self):
        return f'{self.staff.display_name} - {self.service.name}'

    @property
    def price(self):
        return self.custom_price if self.custom_price is not None else self.service.price

    @property
    def duration(self):
        return self.custom_duration if self.custom_duration is not None else self.service.duration


class StaffWorkingHours(models.Model):
    """Working hours for a specific staff member."""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, 'Monday'
        TUESDAY = 1, 'Tuesday'
        WEDNESDAY = 2, 'Wednesday'
        THURSDAY = 3, 'Thursday'
        FRIDAY = 4, 'Friday'
        SATURDAY = 5, 'Saturday'
        SUNDAY = 6, 'Sunday'

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='working_hours',
    )
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_day_off = models.BooleanField(default=False)

    class Meta:
        ordering = ['day_of_week']
        unique_together = ['staff', 'day_of_week']
        verbose_name_plural = 'Staff working hours'

    def __str__(self):
        if self.is_day_off:
            return f'{self.staff.display_name} - {self.get_day_of_week_display()}: Day Off'
        return f'{self.staff.display_name} - {self.get_day_of_week_display()}: {self.start_time} - {self.end_time}'


class StaffTimeOff(models.Model):
    """Time off / vacation for staff members."""

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='time_off',
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)
    is_approved = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date']
        verbose_name_plural = 'Staff time off'

    def __str__(self):
        return f'{self.staff.display_name}: {self.start_date} - {self.end_date}'


commission_percentage = models.DecimalField(
    max_digits=5,
    decimal_places=2,
    default=20
)