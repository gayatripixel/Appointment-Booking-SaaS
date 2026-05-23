from datetime import datetime, timedelta

from django import forms
from django.utils import timezone

from apps.services.models import Service
from apps.staff.models import Staff, StaffWorkingHours, StaffTimeOff

from .models import Booking


class BookingForm(forms.Form):
    """Form for customers to book an appointment."""

    service = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        widget=forms.RadioSelect,
        empty_label=None,
    )
    staff = forms.ModelChoiceField(
        queryset=Staff.objects.none(),
        required=False,
        widget=forms.RadioSelect,
        empty_label=None,
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    time = forms.ChoiceField(
        choices=[],
        widget=forms.RadioSelect,
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any special requests?'}),
    )

    # Guest fields (shown if user not logged in)
    guest_name = forms.CharField(max_length=100, required=False)
    guest_email = forms.EmailField(required=False)
    guest_phone = forms.CharField(max_length=20, required=False)

    def __init__(self, shop, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shop = shop
        self.user = user

        # Set service queryset
        self.fields['service'].queryset = Service.objects.filter(
            shop=shop, is_active=True
        )

        # Set staff queryset
        self.fields['staff'].queryset = Staff.objects.filter(
            shop=shop, is_active=True, accepts_bookings=True
        )

        # Set minimum date to today
        today = timezone.now().date()
        self.fields['date'].widget.attrs['min'] = today.isoformat()

        # Set maximum date (e.g., 30 days ahead)
        max_date = today + timedelta(days=30)
        self.fields['date'].widget.attrs['max'] = max_date.isoformat()

        # If user is logged in, hide guest fields
        if user and user.is_authenticated:
            self.fields['guest_name'].widget = forms.HiddenInput()
            self.fields['guest_email'].widget = forms.HiddenInput()
            self.fields['guest_phone'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        user = self.user
        guest_name = cleaned_data.get('guest_name')
        guest_email = cleaned_data.get('guest_email')

        # Require guest info if not logged in
        if not user or not user.is_authenticated:
            if not guest_name:
                self.add_error('guest_name', 'Name is required.')
            if not guest_email:
                self.add_error('guest_email', 'Email is required.')

        return cleaned_data


class ManualBookingForm(forms.ModelForm):
    """Form for shop owners to manually create bookings (walk-ins, phone bookings)."""

    class Meta:
        model = Booking
        fields = [
            'service', 'staff', 'date', 'start_time',
            'guest_name', 'guest_email', 'guest_phone', 'notes', 'status'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, shop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shop = shop

        self.fields['service'].queryset = Service.objects.filter(shop=shop, is_active=True)
        self.fields['staff'].queryset = Staff.objects.filter(shop=shop, is_active=True)

    def save(self, commit=True):
        booking = super().save(commit=False)
        booking.shop = self.shop

        # Calculate end time based on service duration
        service = booking.service
        start_dt = datetime.combine(booking.date, booking.start_time)
        end_dt = start_dt + timedelta(minutes=service.duration)
        booking.end_time = end_dt.time()

        # Set price from service
        booking.price = service.price

        if commit:
            booking.save()
        return booking


class BookingCancelForm(forms.Form):
    """Form for cancelling a booking."""

    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Reason for cancellation (optional)'
        }),
    )


class BookingStatusForm(forms.Form):
    """Form for updating booking status."""

    status = forms.ChoiceField(choices=Booking.Status.choices)


def get_available_slots(shop, service, staff, date):
    """
    Calculate available time slots for a given service, staff, and date.
    Returns a list of (start_time, end_time) tuples.
    """
    slots = []

    # Get shop business hours for this day
    day_of_week = date.weekday()
    try:
        shop_hours = shop.business_hours.get(day_of_week=day_of_week)
        if shop_hours.is_closed:
            return slots
    except:
        return slots

    # If specific staff requested, check their hours
    if staff:
        try:
            staff_hours = staff.working_hours.get(day_of_week=day_of_week)
            if staff_hours.is_day_off:
                return slots
            open_time = staff_hours.start_time or shop_hours.open_time
            close_time = staff_hours.end_time or shop_hours.close_time
        except StaffWorkingHours.DoesNotExist:
            open_time = shop_hours.open_time
            close_time = shop_hours.close_time

        # Check for time off
        time_off = StaffTimeOff.objects.filter(
            staff=staff,
            start_date__lte=date,
            end_date__gte=date,
        ).exists()
        if time_off:
            return slots
    else:
        open_time = shop_hours.open_time
        close_time = shop_hours.close_time

    if not open_time or not close_time:
        return slots

    # Get service duration
    duration = timedelta(minutes=service.duration)

    # Generate time slots (every 30 minutes)
    slot_interval = timedelta(minutes=30)
    current_time = datetime.combine(date, open_time)
    end_of_day = datetime.combine(date, close_time)

    # Get existing bookings for this date and staff
    if staff:
        existing_bookings = Booking.objects.filter(
            staff=staff,
            date=date,
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        ).values_list('start_time', 'end_time')
    else:
        # If no staff specified, get all bookings for the shop
        existing_bookings = Booking.objects.filter(
            shop=shop,
            date=date,
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        ).values_list('start_time', 'end_time')

    booked_ranges = [(s, e) for s, e in existing_bookings]

    # Check if slot is in the past
    now = timezone.now()
    is_today = date == now.date()

    while current_time + duration <= end_of_day:
        slot_start = current_time.time()
        slot_end = (current_time + duration).time()

        # Skip if slot is in the past
        if is_today and slot_start <= now.time():
            current_time += slot_interval
            continue

        # Check for conflicts with existing bookings
        is_available = True
        for booked_start, booked_end in booked_ranges:
            # Check if there's any overlap
            if not (slot_end <= booked_start or slot_start >= booked_end):
                is_available = False
                break

        if is_available:
            slots.append((slot_start.strftime('%H:%M'), f'{slot_start.strftime("%I:%M %p")}'))

        current_time += slot_interval

    return slots
