from django import forms
from django.utils.text import slugify

from .models import BusinessHours, Shop, ShopClosure


class ShopForm(forms.ModelForm):
    """Form for creating/editing a shop."""

    class Meta:
        model = Shop
        fields = [
            'name', 'description', 'email', 'phone', 'website',
            'address', 'city', 'state', 'postal_code', 'country',
            'logo', 'cover_image',
            'booking_lead_time', 'max_advance_booking_days', 'buffer_time',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Business Name'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your business...'}),
            'email': forms.EmailInput(attrs={'placeholder': 'business@example.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '(555) 123-4567'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourbusiness.com'}),
            'address': forms.TextInput(attrs={'placeholder': '123 Main Street'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'Postal Code'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        slug = slugify(name)

        # Check if slug already exists (excluding current instance)
        qs = Shop.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError('A shop with this name already exists.')

        return name

    def save(self, commit=True):
        shop = super().save(commit=False)
        shop.slug = slugify(shop.name)
        if self.user and not shop.pk:
            shop.owner = self.user
        if commit:
            shop.save()
        return shop


class BusinessHoursForm(forms.ModelForm):
    """Form for editing business hours."""

    class Meta:
        model = BusinessHours
        fields = ['day_of_week', 'open_time', 'close_time', 'is_closed']
        widgets = {
            'open_time': forms.TimeInput(attrs={'type': 'time'}),
            'close_time': forms.TimeInput(attrs={'type': 'time'}),
        }


BusinessHoursFormSet = forms.inlineformset_factory(
    Shop,
    BusinessHours,
    form=BusinessHoursForm,
    extra=7,
    max_num=7,
    can_delete=False,
)


class ShopClosureForm(forms.ModelForm):
    """Form for adding shop closures."""

    class Meta:
        model = ShopClosure
        fields = ['date', 'reason', 'is_full_day', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_full_day = cleaned_data.get('is_full_day')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if not is_full_day:
            if not start_time or not end_time:
                raise forms.ValidationError(
                    'Start and end times are required for partial day closures.'
                )
            if start_time >= end_time:
                raise forms.ValidationError(
                    'End time must be after start time.'
                )

        return cleaned_data
