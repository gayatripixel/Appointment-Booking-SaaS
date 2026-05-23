from django import forms

from apps.accounts.models import User
from apps.services.models import Service

from .models import Staff, StaffService, StaffTimeOff, StaffWorkingHours


class StaffForm(forms.ModelForm):
    """Form for creating/editing staff members."""

    email = forms.EmailField(
        required=True,
        help_text='Staff member will receive an invitation to join.',
    )

    class Meta:
        model = Staff
        fields = ['job_title', 'bio', 'photo', 'is_active', 'accepts_bookings']
        widgets = {
            'job_title': forms.TextInput(attrs={'placeholder': 'e.g., Senior Stylist'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief bio...'}),
        }

    def __init__(self, shop, *args, **kwargs):
        self.shop = shop
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['email'].initial = self.instance.user.email
            self.fields['email'].disabled = True

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()

        if self.instance.pk:
            return email

        # Check if staff already exists for this shop
        existing = Staff.objects.filter(
            shop=self.shop,
            user__email=email
        ).first()
        if existing:
            raise forms.ValidationError('This person is already a staff member.')

        return email

    def save(self, commit=True):
        staff = super().save(commit=False)
        staff.shop = self.shop

        if not self.instance.pk:
            email = self.cleaned_data['email']
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'role': User.Role.STAFF,
                    'is_active': True,
                }
            )
            if not created and user.role == User.Role.CUSTOMER:
                user.role = User.Role.STAFF
                user.save()
            staff.user = user

        if commit:
            staff.save()
        return staff


class StaffServiceForm(forms.Form):
    """Form for assigning services to staff."""

    services = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, staff, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.staff = staff

        services = Service.objects.filter(shop=staff.shop, is_active=True)
        self.fields['services'].choices = [(s.pk, s.name) for s in services]

        current_services = staff.services.values_list('pk', flat=True)
        self.fields['services'].initial = list(current_services)

    def save(self):
        selected = set(map(int, self.cleaned_data['services']))
        current = set(self.staff.services.values_list('pk', flat=True))

        to_add = selected - current
        to_remove = current - selected

        StaffService.objects.filter(staff=self.staff, service_id__in=to_remove).delete()

        for service_id in to_add:
            StaffService.objects.create(staff=self.staff, service_id=service_id)


class StaffWorkingHoursForm(forms.ModelForm):
    """Form for editing staff working hours."""

    class Meta:
        model = StaffWorkingHours
        fields = ['day_of_week', 'start_time', 'end_time', 'is_day_off']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


StaffWorkingHoursFormSet = forms.inlineformset_factory(
    Staff,
    StaffWorkingHours,
    form=StaffWorkingHoursForm,
    extra=7,
    max_num=7,
    can_delete=False,
)


class StaffTimeOffForm(forms.ModelForm):
    """Form for adding staff time off."""

    class Meta:
        model = StaffTimeOff
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.TextInput(attrs={'placeholder': 'e.g., Vacation, Personal'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')

        if start and end and start > end:
            raise forms.ValidationError('End date must be after start date.')

        return cleaned_data
