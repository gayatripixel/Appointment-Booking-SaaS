from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BusinessHoursFormSet, ShopClosureForm, ShopForm
from .models import BusinessHours, Shop, ShopClosure
from django.forms import modelformset_factory
from .forms import BusinessHoursForm

from .forms import ShopClosureForm
from .models import Shop, ShopClosure
from django.shortcuts import render
from .models import Shop


@login_required
def shop_setup_view(request):
    """Shop setup wizard for new shops."""
    # Check if user already has a shop
    existing_shops = get_user_shops(request.user)

    if existing_shops.exists():
     return redirect('shops:list')

    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            shop = form.save()

            # Create default business hours
            for day in range(7):
                is_weekend = day in [5, 6]  # Saturday, Sunday
                BusinessHours.objects.create(
                    shop=shop,
                    day_of_week=day,
                    open_time='09:00' if not is_weekend else None,
                    close_time='17:00' if not is_weekend else None,
                    is_closed=is_weekend,
                )

            # Note: Shop owner permissions are determined by shop.owner relationship,
            # not by elevating user role. This prevents privilege escalation.

            messages.success(request, 'Your shop has been created successfully!')
            return redirect('shops:dashboard', slug=shop.slug)
    else:
        form = ShopForm(user=request.user)

    return render(request, 'shops/setup.html', {'form': form})


# def get_user_shop(user):
#     """Get the shop owned by the user, or None."""
#     return Shop.objects.filter(owner=user).first()

def get_user_shop(user):
    return Shop.objects.filter(owner=user)


@login_required
def shop_setup_view(request):
    """Shop setup wizard for new shops."""
    # Check if user already has a shop
    # existing_shop = get_user_shop(request.user)
    # if existing_shop:
    #     return redirect('shops:dashboard', slug=existing_shop.slug)

    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            shop = form.save()

            # Create default business hours
            for day in range(7):
                is_weekend = day in [5, 6]  # Saturday, Sunday
                BusinessHours.objects.create(
                    shop=shop,
                    day_of_week=day,
                    open_time='09:00' if not is_weekend else None,
                    close_time='17:00' if not is_weekend else None,
                    is_closed=is_weekend,
                )

            # Note: Shop owner permissions are determined by shop.owner relationship,
            # not by elevating user role. This prevents privilege escalation.

            messages.success(request, 'Your shop has been created successfully!')
            return redirect('shops:dashboard', slug=shop.slug)
    else:
        form = ShopForm(user=request.user)

    return render(request, 'shops/setup.html', {'form': form})


@login_required
def shop_dashboard_view(request, slug):
    """Shop owner dashboard."""
    shop = get_object_or_404(Shop, slug=slug)

    # Check ownership
    if shop.owner != request.user:
        raise Http404("Shop not found")

    # Get stats
    context = {
     'shop': shop,
     'all_shops': Shop.objects.filter(owner=request.user),

     'services_count': shop.services.filter(is_active=True).count(),

     'staff_count': shop.staff_members.filter(is_active=True).count(),

     'today_bookings': 0,

     'pending_bookings': 0,
    }

    return render(request, 'shops/dashboard.html', context)


@login_required
def my_shop_redirect_view(request):
    shop = Shop.objects.filter(owner=request.user).first()

    if shop:
        return redirect('shops:dashboard', slug=shop.slug)

    return redirect('shops:setup')

@login_required
def shop_edit_view(request, slug):
    """Edit shop details."""
    shop = get_object_or_404(Shop, slug=slug)

    if shop.owner != request.user:
        raise Http404("Shop not found")

    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=shop, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shop details updated successfully!')
            return redirect('shops:dashboard', slug=shop.slug)
    else:
        form = ShopForm(instance=shop, user=request.user)

    return render(request, 'shops/edit.html', {'form': form, 'shop': shop})


@login_required
def shop_hours_view(request, slug):
    print("HOURS VIEW CALLED")

    shop = get_object_or_404(Shop, slug=slug, owner=request.user)

    BusinessHoursFormSet = modelformset_factory(
        BusinessHours,
        form=BusinessHoursForm,
        extra=0,
        can_delete=False
    )

    queryset = BusinessHours.objects.filter(shop=shop).order_by("day_of_week")

    if request.method == "POST":
        print("POST REQUEST AAYA")

        formset = BusinessHoursFormSet(
            request.POST,
            queryset=queryset
        )

        if formset.is_valid():

            instances = formset.save(commit=False)

            for obj in instances:
                obj.shop = shop
                obj.save()

            messages.success(request, "Business hours updated successfully")
            return redirect("shops:hours", slug=shop.slug)

        else:
            print(formset.errors)

    else:
        formset = BusinessHoursFormSet(queryset=queryset)

    context = {
        "shop": shop,
        "formset": formset,
    }

    return render(request, "shops/hours.html", context)
@login_required
def shop_closures_view(request, slug):
    print("VIEW CALLED")

    shop = get_object_or_404(Shop, slug=slug)

    if request.method == "POST":
        print("POST REQUEST AAYA")

        date = request.POST.get("date")
        reason = request.POST.get("reason")
        is_full_day = request.POST.get("is_full_day") == "on"
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        print(date, reason, is_full_day)

        closure = ShopClosure.objects.create(
            shop=shop,
            date=date,
            reason=reason,
            is_full_day=is_full_day,
            start_time=start_time if not is_full_day else None,
            end_time=end_time if not is_full_day else None,
        )

        print("SAVED:", closure.id)

        return redirect("shops:closures", slug=shop.slug)

    closures = ShopClosure.objects.filter(shop=shop)

    return render(
        request,
        "shops/closures.html",
        {
            "shop": shop,
            "closures": closures,
        },
    )


@login_required
def shop_closure_delete_view(request, slug, pk):
    """Delete a shop closure."""
    shop = get_object_or_404(Shop, slug=slug)

    if shop.owner != request.user:
        raise Http404("Shop not found")

    closure = get_object_or_404(ShopClosure, pk=pk, shop=shop)

    if request.method == 'POST':
        closure.delete()
        messages.success(request, 'Closure deleted successfully!')

    return redirect('shops:closures', slug=shop.slug)


def shop_public_view(request, slug):

    shop = get_object_or_404(Shop, slug=slug, is_active=True)

    services = shop.services.filter(is_active=True).select_related('category')
    staff = shop.staff_members.filter(is_active=True, accepts_bookings=True)
    hours = shop.business_hours.all()

    # ✅ PLAN SESSION ME SAVE KAR
    plan = request.GET.get('plan')
    if plan:
        request.session['plan'] = plan

    return render(request, 'shops/public.html', {
        'shop': shop,
        'services': services,
        'staff': staff,
        'hours': hours,
    })


from django.http import JsonResponse

def shops_list_api(request):
    """API to return all active shops (for frontend React UI)"""

    shops = Shop.objects.filter(is_active=True)

    data = []
    for shop in shops:
        data.append({
            "id": shop.id,
            "name": shop.name,
            "slug": shop.slug,
            "city": shop.city,
            "address": shop.full_address,
            "logo": shop.logo.url if shop.logo else None,
        })

    return JsonResponse(data, safe=False)


def shops_list_view(request):
    """Show all shops in UI (for customers)"""
    shops = Shop.objects.filter(is_active=True)

    return render(request, 'shops/list.html', {
        'shops': shops
    })

@login_required
def my_shop_redirect_view(request):

    shop = Shop.objects.filter(owner=request.user).first()

    if shop:
        return redirect('shops:dashboard', slug=shop.slug)

    return redirect('shops:shop_setup')

@login_required
def add_shop_view(request):

    if request.method == "POST":
        form = ShopForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():

            shop = form.save()

            for day in range(7):
                BusinessHours.objects.create(
                    shop=shop,
                    day_of_week=day,
                    open_time="09:00",
                    close_time="17:00",
                    is_closed=False,
                )

            messages.success(request, "Shop created successfully!")

            return redirect("shops:dashboard", slug=shop.slug)

    else:
        form = ShopForm(user=request.user)

    return render(request, "shops/add_shop.html", {
        "form": form
    })