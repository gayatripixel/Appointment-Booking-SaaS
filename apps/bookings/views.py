import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from apps.bookings.models import Booking
from datetime import datetime, timedelta
from apps.notifications.services import create_notification

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from apps.services.models import Service
from apps.shops.models import Shop
from apps.staff.models import Staff
from django.urls import reverse
from django.http import JsonResponse
from .models import FollowUp

from .forms import (
    BookingCancelForm,
    BookingForm,
    ManualBookingForm,
    get_available_slots,
)
from .models import Booking


stripe.api_key = settings.STRIPE_SECRET_KEY
 

def booking_start_view(request, slug):

    shop = get_object_or_404(Shop, slug=slug, is_active=True)
    services = Service.objects.filter(shop=shop, is_active=True)

    plan = request.GET.get('plan')

    # 🔥 REAL DIFFERENCE

    # BASIC → normal
    if plan == "basic":
        return render(request, 'bookings/start.html', {
            'shop': shop,
            'services': services,
            'plan': plan
        })

    # PRIORITY → skip service → go to staff
    elif plan == "priority":
        first_service = services.first()
        if first_service:
            return redirect('bookings:staff', slug=slug, service_pk=first_service.id)

    # PREMIUM → skip service + staff → go to datetime
    elif plan == "premium":
        first_service = services.first()
        if first_service:
            return redirect('bookings:datetime', slug=slug, service_pk=first_service.id)

    # DEFAULT (no plan)
    return render(request, 'bookings/start.html', {
        'shop': shop,
        'services': services,
        'plan': plan
    })


def booking_staff_view(request, slug, service_pk):
    """Select a staff member for the booking."""
    shop = get_object_or_404(Shop, slug=slug, is_active=True)
    service = get_object_or_404(Service, pk=service_pk, shop=shop, is_active=True)

    # Get staff who can perform this service
    staff_members = Staff.objects.filter(
        shop=shop,
        is_active=True,
        accepts_bookings=True,
        services=service,
    ).select_related('user')

    return render(request, 'bookings/staff.html', {
        'shop': shop,
        'service': service,
        'staff_members': staff_members,
    })


def booking_datetime_view(request, slug, service_pk):
    """Select date and time for the booking."""
    shop = get_object_or_404(Shop, slug=slug, is_active=True)
    service = get_object_or_404(Service, pk=service_pk, shop=shop, is_active=True)

    staff_pk = request.GET.get('staff')
    staff = None
    if staff_pk:
        staff = get_object_or_404(Staff, pk=staff_pk, shop=shop)

    # Default to today
    selected_date = request.GET.get('date')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    # Get available slots
    slots = get_available_slots(shop, service, staff, selected_date)

    # Generate dates for the next 14 days
    today = timezone.now().date()
    dates = [(today + timedelta(days=i)) for i in range(14)]

    return render(request, 'bookings/datetime.html', {
        'shop': shop,
        'service': service,
        'staff': staff,
        'selected_date': selected_date,
        'slots': slots,
        'dates': dates,
    })
   
def booking_confirm_view(request, slug, service_pk):
    """Confirm booking details and submit."""

    shop = get_object_or_404(Shop, slug=slug, is_active=True)
    service = get_object_or_404(
        Service,
        pk=service_pk,
        shop=shop,
        is_active=True
    )

    staff_pk = request.GET.get('staff')
    staff = None

    if staff_pk:
        staff = get_object_or_404(
            Staff,
            pk=staff_pk,
            shop=shop
        )

    date_str = request.GET.get('date')
    time_str = request.GET.get('time')

    if not date_str or not time_str:
        messages.error(request, 'Please select a date and time.')
        return redirect(
            'bookings:datetime',
            slug=slug,
            service_pk=service_pk
        )

    try:
        booking_date = datetime.strptime(
            date_str,
            '%Y-%m-%d'
        ).date()

        booking_time = datetime.strptime(
            time_str,
            '%H:%M'
        ).time()

    except ValueError:
        messages.error(request, 'Invalid date or time.')

        return redirect(
            'bookings:datetime',
            slug=slug,
            service_pk=service_pk
        )

    # Calculate end time
    start_dt = datetime.combine(
        booking_date,
        booking_time
    )

    end_dt = start_dt + timedelta(
        minutes=service.duration
    )

   

    if request.method == 'POST':


           if request.user.is_authenticated:
             user = request.user
           else:
              user = shop.owner

        # Auto assign staff
           if not staff:

            available_staff = Staff.objects.filter(
                shop=shop,
                is_active=True,
                accepts_bookings=True,
                services=service,
            ).first()

            if not available_staff:
                messages.error(
                    request,
                    'No staff available for this service.'
                )

                return redirect(
                    'bookings:start',
                    slug=slug
                )

            staff = available_staff

           booking = Booking.objects.create(
            shop=shop,
            customer=user,
            staff=staff,
            service=service,
            date=booking_date,
            start_time=booking_time,
            end_time=end_dt.time(),


            guest_name=request.POST.get(
                'guest_name',
                ''
            ),



            guest_email=request.POST.get(
                'guest_email',
                ''
            ),

            guest_phone=request.POST.get(
                'guest_phone',
                ''
            ),

            notes=request.POST.get(
                'notes',
                ''
            ),

            price=service.price,

            payment_status='pending',

            status=Booking.Status.CONFIRMED,

        )
           
           create_notification(
               user=shop.owner,
               title="New Appointment",
               message=f"{booking.customer_display_name} booked {booking.service.name}",
               notification_type="booking"
            )

           print("BOOKING CUSTOMER:", booking.customer)


           request.session['recent_booking_id'] = booking.pk
  
           messages.success(
            request,
            'Your booking has been confirmed!'
        )

           return redirect(
            'bookings:success',
            slug=slug,
            pk=booking.pk
          )

    return render(
        request,
        'bookings/confirm.html',
        {
            'shop': shop,
            'service': service,
            'staff': staff,
            'booking_date': booking_date,
            'booking_time': booking_time,
            'end_time': end_dt.time(),
           
        }
    )


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload,
            request.META['HTTP_STRIPE_SIGNATURE'],
            settings.STRIPE_WEBHOOK_SECRET
        )
    except:
        return HttpResponse(status=400)

    # 🔥 PAYMENT SUCCESS EVENT
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        booking_id = session.get("metadata", {}).get("booking_id")

        if booking_id:
            booking = Booking.objects.get(id=booking_id)
            booking.payment_status = "paid"
            booking.status = "completed"
            booking.save()

    return HttpResponse(status=200)
@login_required
def create_booking_checkout(request, slug, service_pk):

    shop = get_object_or_404(
        Shop,
        slug=slug,
        is_active=True
    )

    service = get_object_or_404(
        Service,
        pk=service_pk,
        shop=shop,
        is_active=True
    )

    staff_id = request.GET.get("staff")
    date = request.GET.get("date")
    time = request.GET.get("time")

    success_url = request.build_absolute_uri(
        reverse(
            'bookings:booking_payment_success',
            kwargs={'slug': shop.slug}
        )
    )

    cancel_url = request.build_absolute_uri(
        reverse(
            'bookings:booking_payment_cancel',
            kwargs={'slug': shop.slug}
        )
    )

    checkout_session = stripe.checkout.Session.create(

        payment_method_types=['card'],

        mode='payment',

        line_items=[
            {
                'price_data': {
                    'currency': 'inr',

                    'product_data': {
                        'name': service.name,
                    },

                    'unit_amount': int(service.price * 100),
                },

                'quantity': 1,
            }
        ],

        metadata={
        'user_id': request.user.id if request.user.is_authenticated else '',
        },

success_url=(
    success_url
    + f"?service={service.id}"
    + f"&staff={staff_id}"
    + f"&date={date}"
    + f"&time={time}"
    + "&session_id={CHECKOUT_SESSION_ID}"
),

        cancel_url=cancel_url,
    )

    return redirect(checkout_session.url)

def booking_payment_success(request, slug):

    shop = get_object_or_404(
        Shop,
        slug=slug
    )

    print("PAYMENT SUCCESS PAGE HIT")



    service_id = request.GET.get('service')
    staff_id = request.GET.get('staff')
    date = request.GET.get('date')
    time = request.GET.get('time')

    service = get_object_or_404(
        Service,
        pk=service_id
    )

    staff = get_object_or_404(
        Staff,
        pk=staff_id
    )

    booking_date = datetime.strptime(
        date,
        '%Y-%m-%d'
    ).date()

    booking_time = datetime.strptime(
        time,
        '%H:%M'
    ).time()

    start_dt = datetime.combine(
        booking_date,
        booking_time
    )

    end_dt = start_dt + timedelta(
        minutes=service.duration
    )

    # USER FIX
    user = None

    if request.user.is_authenticated:
        user = request.user

    print("LOGGED IN USER:", user)

    booking = Booking.objects.create(

        shop=shop,

        customer=user,

        staff=staff,

        service=service,

        date=booking_date,

        start_time=booking_time,

        end_time=end_dt.time(),

        price=service.price,

        payment_status='paid',

        status=Booking.Status.CONFIRMED,

    )

    print("CREATING PAYMENT NOTIFICATION")


  
    create_notification(
       user=shop.owner,
       title="Payment Received",
       message=f"₹{booking.price} received from {booking.customer_display_name} for {booking.service.name}",
       notification_type="booking"
    )


    request.session['recent_booking_id'] = booking.pk

    return redirect(
        'bookings:success',
        slug=shop.slug,
        pk=booking.pk
    )




def booking_payment_cancel(request, slug):

    shop = get_object_or_404(
        Shop,
        slug=slug
    )

    return render(
        request,
        'bookings/payment_cancel.html',
        {
            'shop': shop
        }
    )

def booking_success_view(request, slug, pk):
    """Booking confirmation/success page."""
    shop = get_object_or_404(Shop, slug=slug)
    booking = get_object_or_404(Booking, pk=pk, shop=shop)

    # Authorization check - prevent IDOR
    is_authorized = False

    # Check 1: Just created this booking (stored in session)
    if request.session.get('recent_booking_id') == booking.pk:
        is_authorized = True
        # Clear from session after viewing
        del request.session['recent_booking_id']

    # Check 2: Authenticated user is the customer
    elif request.user.is_authenticated and booking.customer == request.user:
        is_authorized = True

    # Check 3: Authenticated user is the shop owner
    elif request.user.is_authenticated and shop.owner == request.user:
        is_authorized = True

    if not is_authorized:
        raise Http404("Booking not found")

    return render(request, 'bookings/success.html', {
        'shop': shop,
        'booking': booking,
    })


# ============================================
# Shop Owner Booking Management Views
# ============================================

def get_shop_for_owner(request, slug):
    """Get shop and verify ownership."""
    shop = get_object_or_404(Shop, slug=slug)
    if shop.owner != request.user:
        raise Http404("Shop not found")
    return shop

@login_required
def payment_success(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    booking.payment_status = "paid"
    booking.status = "completed"
    booking.save()

    return redirect("dashboard")




@login_required
def booking_list_view(request, slug):
    """List all bookings for a shop (owner view)."""
    shop = get_shop_for_owner(request, slug)

    # Filter options
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    staff_filter = request.GET.get('staff', '')

    bookings = Booking.objects.filter(shop=shop).select_related(
        'customer', 'staff__user', 'service'
    )

    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            bookings = bookings.filter(date=filter_date)
        except ValueError:
            pass
    if staff_filter:
        bookings = bookings.filter(staff_id=staff_filter)

    # Default: show upcoming first
    today = timezone.now().date()
    upcoming = bookings.filter(date__gte=today).order_by('date', 'start_time')
    past = bookings.filter(date__lt=today).order_by('-date', '-start_time')

    staff_members = Staff.objects.filter(shop=shop, is_active=True)

    return render(request, 'bookings/manage/list.html', {
        'shop': shop,
        'upcoming_bookings': upcoming,
        'past_bookings': past,
        'staff_members': staff_members,
        'status_choices': Booking.Status.choices,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'staff_filter': staff_filter,
    })


@login_required
def booking_detail_view(request, slug, pk):
    """View booking details (owner view)."""
    shop = get_shop_for_owner(request, slug)
    booking = get_object_or_404(Booking, pk=pk, shop=shop)

    return render(request, 'bookings/manage/detail.html', {
        'shop': shop,
        'booking': booking,
    })


@login_required
def booking_create_view(request, slug):
    """Manually create a booking (walk-in, phone booking)."""
    shop = get_shop_for_owner(request, slug)

    if request.method == 'POST':
        form = ManualBookingForm(shop, request.POST)
        if form.is_valid():
            booking = form.save()
            messages.success(request, 'Booking created successfully!')
            return redirect('bookings:manage_list', slug=shop.slug)
    else:
        form = ManualBookingForm(shop)

    return render(request, 'bookings/manage/form.html', {
        'shop': shop,
        'form': form,
        'title': 'Create Booking',
    })

@login_required
def add_followup_view(request):
    pass

@login_required
@require_POST
def booking_status_view(request, slug, pk):
    """Update booking status."""
    shop = get_shop_for_owner(request, slug)
    booking = get_object_or_404(Booking, pk=pk, shop=shop)

    new_status = request.POST.get('status')
    if new_status in dict(Booking.Status.choices):
        booking.status = new_status
        booking.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Booking marked as {booking.get_status_display()}.')

    return redirect('bookings:manage_detail', slug=slug, pk=pk)


@login_required
def booking_cancel_view(request, slug, pk):
    """Cancel a booking (owner view)."""
    shop = get_shop_for_owner(request, slug)
    booking = get_object_or_404(Booking, pk=pk, shop=shop)

    if not booking.can_cancel:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('bookings:manage_detail', slug=slug, pk=pk)

    if request.method == 'POST':
        form = BookingCancelForm(request.POST)
        if form.is_valid():
            booking.cancel(form.cleaned_data.get('reason', ''))
            messages.success(request, 'Booking has been cancelled.')
            return redirect('bookings:manage_list', slug=shop.slug)
    else:
        form = BookingCancelForm()

    return render(request, 'bookings/manage/cancel.html', {
        'shop': shop,
        'booking': booking,
        'form': form,
    })


# ============================================
# Customer Booking Management Views
# ============================================

@login_required
def my_bookings_view(request):
    """View customer's own bookings."""
    bookings = Booking.objects.filter(
        customer=request.user
    ).select_related('shop', 'staff__user', 'service').order_by('-date', '-start_time')

    today = timezone.now().date()
    upcoming = [b for b in bookings if b.date >= today and b.status in ['pending', 'confirmed']]
    past = [b for b in bookings if b.date < today or b.status in ['completed', 'cancelled', 'no_show']]

    return render(request, 'bookings/my_bookings.html', {
        'upcoming_bookings': upcoming,
        'past_bookings': past,
    })


@login_required
def my_booking_cancel_view(request, pk):
    """Cancel customer's own booking."""
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)

    if not booking.can_cancel:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('bookings:my_bookings')

    if request.method == 'POST':
        booking.cancel('Cancelled by customer')
        messages.success(request, 'Your booking has been cancelled.')
        return redirect('bookings:my_bookings')

    return render(request, 'bookings/my_booking_cancel.html', {
        'booking': booking,
    })


# ============================================
# HTMX / API Views
# ============================================

@ratelimit(key='ip', rate='60/m', block=True)
def slots_api_view(request, slug):
    """API endpoint to get available slots for a date (used with HTMX)."""
    shop = get_object_or_404(Shop, slug=slug, is_active=True)

    service_pk = request.GET.get('service')
    staff_pk = request.GET.get('staff')
    date_str = request.GET.get('date')

    if not service_pk or not date_str:
        return render(request, 'bookings/partials/slots.html', {'slots': []})

    try:
        service = Service.objects.get(pk=service_pk, shop=shop)
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (Service.DoesNotExist, ValueError):
        return render(request, 'bookings/partials/slots.html', {'slots': []})

    staff = None
    if staff_pk:
        try:
            staff = Staff.objects.get(pk=staff_pk, shop=shop)
        except Staff.DoesNotExist:
            pass

    slots = get_available_slots(shop, service, staff, selected_date)

    return render(request, 'bookings/partials/slots.html', {
        'slots': slots,
        'service': service,
        'staff': staff,
        'selected_date': selected_date,
    })

@login_required
def add_followup_view(request):

    bookings = Booking.objects.all()

    if request.method == "POST":

        booking_id = request.POST.get("booking")
        followup_date = request.POST.get("followup_date")
        followup_time = request.POST.get("followup_time")
        notes = request.POST.get("notes")

        booking = Booking.objects.get(id=booking_id)

        FollowUp.objects.create(
            booking=booking,
            followup_date=followup_date,
            followup_time=followup_time,
            notes=notes
        )

        messages.success(request, "Follow Up Added Successfully")

        return redirect("dashboard:index")

    return render(
        request,
        "bookings/add_followup.html",
        {
            "bookings": bookings
        }
    )

