from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Shop(models.Model):
    """Model representing a shop/business."""


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_shops',
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    # Contact Information
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)

    # Address
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='USA')

    # Media
    logo = models.ImageField(upload_to='shops/logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='shops/covers/', blank=True, null=True)

    # Settings
    is_active = models.BooleanField(default=True)
    accepts_online_booking = models.BooleanField(default=True)
    booking_lead_time = models.PositiveIntegerField(
        default=60,
        help_text='Minimum minutes before an appointment can be booked',
    )
    max_advance_booking_days = models.PositiveIntegerField(
        default=30,
        help_text='Maximum days in advance a booking can be made',
    )
    buffer_time = models.PositiveIntegerField(
        default=0,
        help_text='Buffer time in minutes between appointments',
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shops:detail', kwargs={'slug': self.slug})

    @property
    def full_address(self):
        parts = [self.address, self.city]
        if self.state:
            parts.append(self.state)
        parts.append(self.postal_code)
        return ', '.join(parts)


class BusinessHours(models.Model):
    """Model for shop business hours."""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, 'Monday'
        TUESDAY = 1, 'Tuesday'
        WEDNESDAY = 2, 'Wednesday'
        THURSDAY = 3, 'Thursday'
        FRIDAY = 4, 'Friday'
        SATURDAY = 5, 'Saturday'
        SUNDAY = 6, 'Sunday'

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='business_hours',
    )
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ['day_of_week']
        unique_together = ['shop', 'day_of_week']
        verbose_name_plural = 'Business hours'

    def __str__(self):
        if self.is_closed:
            return f'{self.shop.name} - {self.get_day_of_week_display()}: Closed'
        return f'{self.shop.name} - {self.get_day_of_week_display()}: {self.open_time} - {self.close_time}'


class ShopClosure(models.Model):
    """Model for shop closures (holidays, special days)."""

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='closures',
    )
    date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)
    is_full_day = models.BooleanField(default=True)
    start_time = models.TimeField(
        null=True, 
        blank=True
    )
    end_time = models.TimeField(
        null=True, 
        blank=True
    )

    class Meta:
        ordering = ['date']
        unique_together = ['shop', 'date']

    def __str__(self):
        return f'{self.shop.name} - {self.date}: {self.reason or "Closed"}'
