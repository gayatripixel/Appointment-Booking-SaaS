from django.contrib import admin

from .models import Service, ServiceCategory


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'order')
    list_filter = ('shop',)
    search_fields = ('name', 'shop__name')
    ordering = ('shop', 'order', 'name')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'category', 'duration', 'price', 'is_active')
    list_filter = ('shop', 'category', 'is_active')
    search_fields = ('name', 'shop__name')
    ordering = ('shop', 'order', 'name')

    fieldsets = (
        (None, {
            'fields': ('shop', 'category', 'name', 'description')
        }),
        ('Pricing & Duration', {
            'fields': ('duration', 'price')
        }),
        ('Advanced Settings', {
            'fields': ('buffer_before', 'buffer_after', 'max_bookings_per_slot'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'order')
        }),
    )
