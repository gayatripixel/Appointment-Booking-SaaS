from django.db import models

from apps.shops.models import Shop


class ServiceCategory(models.Model):
    """Category for grouping services."""

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='service_categories',
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        unique_together = ['shop', 'name']
        verbose_name_plural = 'Service categories'

    def __str__(self):
        return f'{self.shop.name} - {self.name}'


class Service(models.Model):
    """Model representing a service offered by a shop."""

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='services',
        
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services',
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(help_text='Duration in minutes')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Optional settings
    buffer_before = models.PositiveIntegerField(
        default=0,
        help_text='Buffer time before appointment in minutes',
    )
    buffer_after = models.PositiveIntegerField(
        default=0,
        help_text='Buffer time after appointment in minutes',
    )
    max_bookings_per_slot = models.PositiveIntegerField(
        default=1,
        help_text='Maximum concurrent bookings for this service',
    )

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.name} ({self.shop.name})'

    @property
    def total_duration(self):
        """Total time including buffers."""
        return self.buffer_before + self.duration + self.buffer_after

    @property
    def formatted_price(self):
        return f'₹{self.price:.2f}'

    @property
    def formatted_duration(self):
        if self.duration >= 60:
            hours = self.duration // 60
            minutes = self.duration % 60
            if minutes:
                return f'{hours}h {minutes}min'
            return f'{hours}h'
        return f'{self.duration}min'
