from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from apps.shops.models import Shop
from django.db.models import Count

from .forms import ServiceCategoryForm, ServiceForm
from .models import Service, ServiceCategory
from django.http import JsonResponse

def get_shop_for_user(request, slug):
    """Get shop and verify ownership."""
    shop = get_object_or_404(Shop, slug=slug)
    if shop.owner != request.user:
        raise Http404("Shop not found")
    return shop


@login_required
def service_list_view(request, slug):
    """List all services for a shop."""
    shop = get_shop_for_user(request, slug)

    services = Service.objects.filter(shop=shop).select_related('category').annotate(
       bookings_count=Count('bookings', distinct=True)
    )
    
    categories = shop.service_categories.all()

    # return render(request, 'shops/list.html', {
    return render(request, 'services/service.html', {
        'shop': shop,
        'services': services,
        'categories': categories,
    })


@login_required
def service_create_view(request, slug):
    """Create a new service."""
    shop = get_shop_for_user(request, slug)

    if request.method == 'POST':
        form = ServiceForm(shop, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service created successfully!')
            return redirect('services:list', slug=shop.slug)
    else:
        form = ServiceForm(shop)

    return render(request, 'services/form.html', {
        'shop': shop,
        'form': form,
        'title': 'Add Service',
    })


@login_required
def service_edit_view(request, slug, pk):
    """Edit an existing service."""
    shop = get_shop_for_user(request, slug)
    service = get_object_or_404(Service, pk=pk, shop=shop)

    if request.method == 'POST':
        form = ServiceForm(shop, request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('services:list', slug=shop.slug)
    else:
        form = ServiceForm(shop, instance=service)

    return render(request, 'services/form.html', {
        'shop': shop,
        'form': form,
        'service': service,
        'title': 'Edit Service',
    })


@login_required
def service_delete_view(request, slug, pk):
    """Delete a service."""
    shop = get_shop_for_user(request, slug)
    service = get_object_or_404(Service, pk=pk, shop=shop)

    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully!')

    return redirect('services:list', slug=shop.slug)

@login_required
def service_toggle_status(request, slug, pk):
    shop = get_shop_for_user(request, slug)
    service = get_object_or_404(Service, pk=pk, shop=shop)

    service.is_active = not service.is_active
    service.save()

    return JsonResponse({
        "success": True,
        "is_active": service.is_active
    })

@login_required
def category_create_view(request, slug):
    """Create a new service category."""
    shop = get_shop_for_user(request, slug)

    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.shop = shop
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('services:list', slug=shop.slug)
    else:
        form = ServiceCategoryForm()

    return render(request, 'services/category_form.html', {
        'shop': shop,
        'form': form,
        'title': 'Add Category',
    })


@login_required
def category_edit_view(request, slug, pk):
    """Edit a service category."""
    shop = get_shop_for_user(request, slug)
    category = get_object_or_404(ServiceCategory, pk=pk, shop=shop)

    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('services:list', slug=shop.slug)
    else:
        form = ServiceCategoryForm(instance=category)

    return render(request, 'services/category_form.html', {
        'shop': shop,
        'form': form,
        'category': category,
        'title': 'Edit Category',
    })


@login_required
def category_delete_view(request, slug, pk):
    """Delete a service category."""
    shop = get_shop_for_user(request, slug)
    category = get_object_or_404(ServiceCategory, pk=pk, shop=shop)

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')

    return redirect('services:list', slug=shop.slug)


@login_required
def all_services_view(request):
    services = Service.objects.filter(
        shop__owner=request.user
    ).select_related('shop', 'category')

    # CATEGORY FILTER
    category = request.GET.get("category")

    if category:
        services = services.filter(
            category__name=category
        )

    # SEARCH FILTER
    search = request.GET.get("search")

    if search:
        services = services.filter(
            name__icontains=search
        )

    categories = ServiceCategory.objects.filter(
        shop__owner=request.user
    )

    return render(request, 'services/all_services.html', {
        'services': services,
        'categories': categories,
    })
