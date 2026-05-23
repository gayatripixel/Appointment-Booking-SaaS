from django import forms

from .models import Service, ServiceCategory


class ServiceCategoryForm(forms.ModelForm):
    """Form for creating/editing service categories."""

    class Meta:
        model = ServiceCategory
        fields = ['name', 'description', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Category Name'}),
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Description (optional)'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }


class ServiceForm(forms.ModelForm):
    """Form for creating/editing services."""

    class Meta:
        model = Service
        fields = [
            'category', 'name', 'description', 'duration', 'price',
            'buffer_before', 'buffer_after', 'is_active', 'order',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Service Name'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe this service...'}),
            'duration': forms.NumberInput(attrs={'min': 5, 'step': 5, 'placeholder': '30'}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'placeholder': '25.00'}),
            'buffer_before': forms.NumberInput(attrs={'min': 0, 'step': 5}),
            'buffer_after': forms.NumberInput(attrs={'min': 0, 'step': 5}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, shop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shop = shop
        self.fields['category'].queryset = ServiceCategory.objects.filter(shop=shop)
        self.fields['category'].required = False

    def save(self, commit=True):
        service = super().save(commit=False)
        service.shop = self.shop
        if commit:
            service.save()
        return service
