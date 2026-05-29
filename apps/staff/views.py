from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import render
from apps.shops.models import Shop

from .forms import (
    StaffForm,
    StaffServiceForm,
    StaffTimeOffForm,
    StaffWorkingHoursFormSet,
)
from .models import Staff, StaffTimeOff, StaffWorkingHours
from django.db.models import Sum



def get_shop_for_user(request, slug):
    """Get shop and verify ownership."""
    shop = get_object_or_404(Shop, slug=slug)
    if shop.owner != request.user:
        raise Http404("Shop not found")
    return shop


@login_required
def staff_list_view(request, slug):
    """List all staff for a shop."""
    shop = get_shop_for_user(request, slug)
    staff_members = shop.staff_members.select_related('user').all()

    return render(request, 'staff/list.html', {
        'shop': shop,
        'staff_members': staff_members,
    })


@login_required
def staff_create_view(request, slug):
    """Add a new staff member."""
    shop = get_shop_for_user(request, slug)

    if request.method == 'POST':
        form = StaffForm(shop, request.POST, request.FILES)
        if form.is_valid():
            staff = form.save()

            # Create default working hours
            for day in range(7):
                is_weekend = day in [5, 6]
                StaffWorkingHours.objects.create(
                    staff=staff,
                    day_of_week=day,
                    start_time='09:00' if not is_weekend else None,
                    end_time='17:00' if not is_weekend else None,
                    is_day_off=is_weekend,
                )

            messages.success(request, 'Staff member added successfully!')
            return redirect('staff:list', slug=shop.slug)
    else:
        form = StaffForm(shop)

    return render(request, 'staff/form.html', {
        'shop': shop,
        'form': form,
        'title': 'Add Staff Member',
    })


@login_required
def staff_edit_view(request, slug, pk):
    """Edit a staff member."""
    shop = get_shop_for_user(request, slug)
    staff = get_object_or_404(Staff, pk=pk, shop=shop)

    if request.method == 'POST':
        form = StaffForm(shop, request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff member updated successfully!')
            return redirect('staff:list', slug=shop.slug)
    else:
        form = StaffForm(shop, instance=staff)

    return render(request, 'staff/form.html', {
        'shop': shop,
        'form': form,
        'staff': staff,
        'title': 'Edit Staff Member',
    })


@login_required
def staff_delete_view(request, slug, pk):
    """Delete a staff member."""
    shop = get_shop_for_user(request, slug)
    staff = get_object_or_404(Staff, pk=pk, shop=shop)

    if request.method == 'POST':
        staff.delete()
        messages.success(request, 'Staff member removed successfully!')

    return redirect('staff:list', slug=shop.slug)


@login_required
def staff_services_view(request, slug, pk):
    """Assign services to a staff member."""
    shop = get_shop_for_user(request, slug)
    staff = get_object_or_404(Staff, pk=pk, shop=shop)

    if request.method == 'POST':
        form = StaffServiceForm(staff, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Services updated successfully!')
            return redirect('staff:services', slug=shop.slug, pk=staff.pk)
    else:
        form = StaffServiceForm(staff)

    return render(request, 'staff/services.html', {
        'shop': shop,
        'staff': staff,
        'form': form,
    })


@login_required
def staff_hours_view(request, slug, pk):
    """Edit working hours for a staff member."""
    shop = get_shop_for_user(request, slug)
    staff = get_object_or_404(Staff, pk=pk, shop=shop)

    if request.method == 'POST':
        formset = StaffWorkingHoursFormSet(request.POST, instance=staff)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Working hours updated successfully!')
            return redirect('staff:hours', slug=shop.slug, pk=staff.pk)
    else:
        existing_days = set(staff.working_hours.values_list('day_of_week', flat=True))
        for day in range(7):
            if day not in existing_days:
                StaffWorkingHours.objects.create(staff=staff, day_of_week=day, is_day_off=True)

        formset = StaffWorkingHoursFormSet(instance=staff)

    return render(request, 'staff/hours.html', {
        'shop': shop,
        'staff': staff,
        'formset': formset,
    })


@login_required
def staff_time_off_view(request, slug, pk):
    """Manage time off for a staff member."""
    shop = get_shop_for_user(request, slug)
    staff = get_object_or_404(Staff, pk=pk, shop=shop)
    time_off_list = staff.time_off.all()

    if request.method == 'POST':
        form = StaffTimeOffForm(request.POST)
        if form.is_valid():
            time_off = form.save(commit=False)
            time_off.staff = staff
            time_off.save()
            messages.success(request, 'Time off added successfully!')
            return redirect('staff:time_off', slug=shop.slug, pk=staff.pk)
    else:
        form = StaffTimeOffForm()

    return render(request, 'staff/time_off.html', {
        'shop': shop,
        'staff': staff,
        'time_off_list': time_off_list,
        'form': form,
    })


@login_required
def staff_time_off_delete_view(request, slug, pk, time_off_pk):
    """Delete a time off entry."""
    shop = get_shop_for_user(request, slug)
    staff = get_object_or_404(Staff, pk=pk, shop=shop)
    time_off = get_object_or_404(StaffTimeOff, pk=time_off_pk, staff=staff)

    if request.method == 'POST':
        time_off.delete()
        messages.success(request, 'Time off deleted successfully!')

    return redirect('staff:time_off', slug=shop.slug, pk=staff.pk)

@login_required
def staff_shop_select_view(request):

    shops = Shop.objects.filter(owner=request.user)

    return render(request, 'staff/shop_select.html', {
        'shops': shops
    })
