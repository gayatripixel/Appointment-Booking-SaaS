from django.contrib import admin

from .models import BusinessHours, Shop, ShopClosure


class BusinessHoursInline(admin.TabularInline):
    model = BusinessHours
    extra = 0
    max_num = 7


class ShopClosureInline(admin.TabularInline):
    model = ShopClosure
    extra = 0


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'city', 'is_active', 'accepts_online_booking')
    list_filter = ('is_active', 'accepts_online_booking', 'city')
    search_fields = ('name', 'owner__email', 'city')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [BusinessHoursInline, ShopClosureInline]

    fieldsets = (
        (None, {
            'fields': ('owner', 'name', 'slug', 'description')
        }),
        ('Contact', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Media', {
            'fields': ('logo', 'cover_image')
        }),
        ('Settings', {
            'fields': (
                'is_active',
                'accepts_online_booking',
                'booking_lead_time',
                'max_advance_booking_days',
                'buffer_time',
            )
        }),
    )


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ('shop', 'day_of_week', 'open_time', 'close_time', 'is_closed')
    list_filter = ('shop', 'day_of_week', 'is_closed')


@admin.register(ShopClosure)
class ShopClosureAdmin(admin.ModelAdmin):
    list_display = ('shop', 'date', 'reason', 'is_full_day')
    list_filter = ('shop', 'is_full_day')
    date_hierarchy = 'date'
