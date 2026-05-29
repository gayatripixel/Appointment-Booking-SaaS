from django.contrib import admin

from .models import Booking, FollowUp


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_display_name', 'service', 'staff',
        'date', 'start_time', 'status', 'created_at'
    ]
    list_filter = ['status', 'date', 'shop', 'staff']
    search_fields = [
        'customer__email', 'customer__first_name', 'customer__last_name',
        'guest_name', 'guest_email', 'service__name'
    ]
    date_hierarchy = 'date'
    ordering = ['-date', '-start_time']

    fieldsets = (
        (None, {
            'fields': ('shop', 'service', 'staff', 'status')
        }),
        ('Schedule', {
            'fields': ('date', 'start_time', 'end_time', 'price')
        }),
        ('Customer', {
            'fields': ('customer', 'guest_name', 'guest_email', 'guest_phone')
        }),
        ('Additional Info', {
            'fields': ('notes', 'cancellation_reason'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def customer_display_name(self, obj):
        return obj.customer_display_name
    customer_display_name.short_description = 'Customer'
@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'booking',
        'followup_date',
        'is_completed',
        'created_at'
    ]

    list_filter = [
        'is_completed',
        'followup_date'
    ]

    search_fields = [
        'booking__guest_name',
        'booking__guest_email'
    ]

    ordering = ['followup_date']
