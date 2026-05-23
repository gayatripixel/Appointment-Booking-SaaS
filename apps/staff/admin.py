from django.contrib import admin

from .models import Staff, StaffService, StaffTimeOff, StaffWorkingHours


class StaffServiceInline(admin.TabularInline):
    model = StaffService
    extra = 1


class StaffWorkingHoursInline(admin.TabularInline):
    model = StaffWorkingHours
    extra = 0
    max_num = 7


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'shop', 'job_title', 'is_active', 'accepts_bookings')
    list_filter = ('shop', 'is_active', 'accepts_bookings')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'shop__name')
    inlines = [StaffServiceInline, StaffWorkingHoursInline]

    fieldsets = (
        (None, {
            'fields': ('user', 'shop', 'job_title', 'bio', 'photo')
        }),
        ('Settings', {
            'fields': ('is_active', 'accepts_bookings')
        }),
    )


@admin.register(StaffService)
class StaffServiceAdmin(admin.ModelAdmin):
    list_display = ('staff', 'service', 'custom_price', 'custom_duration')
    list_filter = ('staff__shop', 'service')


@admin.register(StaffWorkingHours)
class StaffWorkingHoursAdmin(admin.ModelAdmin):
    list_display = ('staff', 'day_of_week', 'start_time', 'end_time', 'is_day_off')
    list_filter = ('staff__shop', 'day_of_week', 'is_day_off')


@admin.register(StaffTimeOff)
class StaffTimeOffAdmin(admin.ModelAdmin):
    list_display = ('staff', 'start_date', 'end_date', 'reason', 'is_approved')
    list_filter = ('staff__shop', 'is_approved')
    date_hierarchy = 'start_date'
