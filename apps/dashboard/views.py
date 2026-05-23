import stripe
from django.conf import settings
from apps.staff.models import Staff
from django.db.models import Avg

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta
import random

from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.utils import timezone

from django.db import models

from apps.shops.models import Shop
from apps.bookings.models import Booking
from django.db.models import Count
from apps.services.models import Service
from django.db.models.functions import ExtractWeekDay

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from apps.bookings.models import Booking
from apps.accounts.models import User
from django.db.models import Sum
from datetime import datetime

from django.db.models.functions import ExtractMonth
from django.db.models import Sum, Count


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(request, plan):

    if plan == "priority":
        amount = 29900
        plan_name = "Priority Booking"

    elif plan == "premium":
        amount = 99900
        plan_name = "Premium Experience"

    else:
        amount = 0
        plan_name = "Basic"

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        mode='payment',

       

        line_items=[
            {
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': plan_name,
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }
        ],

        success_url=f'http://127.0.0.1:8000/dashboard/payment-success/?plan={plan}',

        cancel_url='http://127.0.0.1:8000/dashboard/payment-cancel/',
    )

    return redirect(checkout_session.url)

def get_mock_data_for_month(month_offset=0):
    """Generate consistent mock data for a given month offset (0 = current month, -1 = last month, etc.)"""
    # Use month_offset as seed for consistent random data per month
    random.seed(42 + month_offset)
    
    base_revenue = 8000 + (month_offset * 500)
    base_bookings = 80 + (month_offset * 5)
    base_customers = 1200 + (month_offset * 50)
    
    stats = {
        'today_appointments': random.randint(8, 18),
        'upcoming_bookings': random.randint(35, 60),
        'total_customers': base_customers + random.randint(0, 100),
        'monthly_revenue': base_revenue + random.randint(0, 4000),
        'today_change': random.randint(5, 25),
        'bookings_change': random.randint(-5, 15),
        'customers_change': random.randint(5, 20),
        'revenue_change': random.randint(10, 35),
    }
    
    # Reset seed for other random data
    random.seed()
    
    return stats


@login_required
def index_view(request):

    shops = Shop.objects.filter(owner=request.user)
    selected_shop_id = request.GET.get('shop')

    shop = None
    if selected_shop_id:
        shop = shops.filter(id=selected_shop_id).first()
    if not shop:
        shop = shops.first()

    today = datetime.now()

    # SERVICES
    services = []
    if shop:
        services_qs = Service.objects.filter(shop=shop)
        colors = ['#533483', '#7c4dab', '#e94560', '#f06b7e', '#f8a5b3']

        for i, service in enumerate(services_qs):
            bookings_count = Booking.objects.filter(service=service).count()
            services.append({
                'name': service.name,
                'count': bookings_count if bookings_count > 0 else 1,
                'price': service.price,
                'color': colors[i % len(colors)]
            })

    # MONTH FILTER
    selected_month_offset = int(request.GET.get('month', 0))


    selected_date = today


    for _ in range(abs(selected_month_offset)):
        if selected_month_offset < 0:
            selected_date = selected_date.replace(day=1) - timedelta(days=1)

    selected_month_name = selected_date.strftime('%B %Y')

    # AVAILABLE MONTHS
    available_months = []
    temp_date = today
    for i in range(6):
        available_months.append({
            'offset': -i,
            'name': temp_date.strftime('%B %Y'),
            'short_name': temp_date.strftime('%b %Y'),
        })
        temp_date = temp_date.replace(day=1) - timedelta(days=1)

    # GRAPH DATA
    months = []
    revenue_data = []
    bookings_data = []

    random.seed(100 + selected_month_offset)
    for i in range(5, -1, -1):
        month_date = selected_date - timedelta(days=30*i)
        months.append(month_date.strftime('%b'))
        revenue_data.append(random.randint(2500, 8500))
        bookings_data.append(random.randint(45, 120))
    random.seed()

    # WEEKLY DATA
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekly_appointments = []

    for i in range(7):
        if shop:
            count = Booking.objects.filter(shop=shop).count()
        else:
            count = 0
        weekly_appointments.append(count)

    # ACTIVITIES
    activities = [
        {'title': 'New booking confirmed', 'description': 'Gayatri booked Haircut'},
        {'title': 'Payment received', 'description': '₹850 received'},
    ]

    # UPCOMING
    upcoming = [
        {'time': '09:00 AM', 'customer': 'Atul', 'service': 'Haircut'},
        {'time': '10:00 AM', 'customer': 'Swarnim', 'service': 'Massage'},
    ]

    # STATS
    if shop:
        today_appointments = Booking.objects.filter(shop=shop, date=today.date()).count()
        total_bookings = Booking.objects.filter(shop=shop).count()
        total_revenue = Booking.objects.filter(shop=shop).aggregate(total=models.Sum('price'))['total'] or 0
    else:
        today_appointments = 0
        total_bookings = 0
        total_revenue = 0

    stats = {
        'today_appointments': today_appointments,
        'upcoming_bookings': total_bookings,
        'monthly_revenue': total_revenue,
    }

    # CONTEXT
    context = {
        'selected_month_name': selected_month_name,
        'selected_month_offset': selected_month_offset,
        'available_months': available_months,
        'months': months,
        'revenue_data': revenue_data,
        'bookings_data': bookings_data,
        'days': days,
        'weekly_appointments': weekly_appointments,
        'services': services,
        'activities': activities,
        'upcoming': upcoming,
        'stats': stats,
        'shops': shops,
        'selected_shop': shop,
    }

    return render(request, 'dashboard/index.html', context)


def dashboard_data(request):
    today = datetime.today().date()
    total_appointments = Booking.objects.filter(date=today).count()
    upcoming_bookings = Booking.objects.filter(date__gt=today).count()
    total_customers = User.objects.count()
    revenue = Booking.objects.aggregate(total=Sum('price'))['total'] or 0

    # 🔹 MONTHLY REVENUE
    monthly_data = [0] * 12
    monthly_qs = (
        Booking.objects
        .annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(total=Sum('price'))
    )
    for item in monthly_qs:
        monthly_data[item['month'] - 1] = item['total'] or 0

    # 🔹 WEEKLY DATA
    weekly_data = [0] * 7
    weekly_qs = (
        Booking.objects
        .annotate(day=ExtractWeekDay('date'))
        .values('day')
        .annotate(count=Count('id'))
    )
    for w in weekly_qs:
        weekly_data[w['day'] - 1] = w['count']

    # 🔹 POPULAR SERVICES
    popular_services = [
        {"name": "Glow Salon - Haircut", "count": 120, "color": "#533483"},
        {"name": "Glow Salon - Facial", "count": 80, "color": "#7c4dab"},
        {"name": "Relax Spa & Massage - Massage", "count": 95, "color": "#e94560"},
        {"name": "Relax Spa - Therapy", "count": 60, "color": "#fb7185"},
        {"name": "Dr Care Clinic - General Consultation", "count": 70, "color": "#34d399"},
    ]

    
    today_bookings = (
        Booking.objects
        .filter(date=today)
        .select_related('service', 'customer')
        .order_by('start_time')
    )

    today_schedule = [
    {
        "time": "09:30 AM - 10:30 AM",
        "customer": "Rahul Sharma",
        "service": "Haircut",
        "status": "Confirmed"
    },
    {
        "time": "11:00 AM - 12:00 PM",
        "customer": "Priya Patel",
        "service": "Facial",
        "status": "In Progress"
    },
    {
        "time": "01:00 PM - 02:00 PM",
        "customer": "Amit Verma",
        "service": "Massage",
        "status": "Confirmed"
    },
    {
        "time": "03:30 PM - 04:00 PM",
        "customer": "Sneha Kulkarni",
        "service": "Consultation",
        "status": "Upcoming"
    }
]
    
    

    # ✅ IMPORTANT: Ye function ke andar hona chahiye
    return JsonResponse({
        "todayAppointments": total_appointments,
        "upcomingBookings": upcoming_bookings,
        "totalCustomers": total_customers,
        "revenue": revenue,
        "monthlyRevenue": monthly_data,
        "weeklyData": weekly_data,
        "popularServices": popular_services,
        "todaySchedule": today_schedule
    })


@login_required
def appointments_view(request):

    shops = Shop.objects.filter(owner=request.user)

    selected_shop = shops.first()

    selected_shop_id = request.GET.get('shop')

    selected_shop = None

    if selected_shop_id:
      selected_shop = shops.filter(id=selected_shop_id).first()

    if not selected_shop:
      selected_shop = shops.first()

    bookings = Booking.objects.filter(
    #   shop__in=shops
        shop=selected_shop
    ).select_related(
     'customer',
     'service',
     'staff',
     'shop'
    ).order_by('-date', '-start_time')

    stats = {
        'total': bookings.count(),
        'confirmed': bookings.filter(status='confirmed').count(),
        'pending': bookings.filter(status='pending').count(),
        'completed': bookings.filter(status='completed').count(),
    }

    bookings = Booking.objects.filter(
    shop__in=shops
    ).select_related(
        'customer',
        'staff__user',
        'service'
    ).order_by('-date', '-start_time')

    # =========================
    # SEARCH
    # =========================

    search = request.GET.get('search')

    if search:
        bookings = bookings.filter(
            service__name__icontains=search
        )

    # =========================
    # STATUS FILTER
    # =========================

    status = request.GET.get('status')

    if status:
        bookings = bookings.filter(status=status)

    # =========================
    # STATS
    # =========================

    total_bookings = bookings.count()

    confirmed_count = bookings.filter(
        status='confirmed'
    ).count()

    pending_count = bookings.filter(
        status='pending'
    ).count()

    completed_count = bookings.filter(
        status='completed'
    ).count()

    revenue = bookings.filter(
        payment_status='paid'
    ).aggregate(
        total=Sum('price')
    )['total'] or 0

    # =========================
    # PAGINATION
    # =========================

    paginator = Paginator(bookings, 10)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/appointments.html', {

        'shops': shops,

        'selected_shop': selected_shop,

        'page_obj': page_obj,

        'bookings': page_obj,

        'total_bookings': total_bookings,

        'confirmed_count': confirmed_count,

        'pending_count': pending_count,

        'completed_count': completed_count,

        'revenue': revenue,

    })


@login_required
def services_view(request):

    services = Service.objects.all().select_related('category')

    search = request.GET.get("search")
    category = request.GET.get("category")

    if search:
        services = services.filter(
            name__icontains=search
        )

    if category:
        services = services.filter(
            category__name=category
        )

    # Categories
    categories = (
        services
        .values_list('category__name', flat=True)
        .distinct()
    )

    # Stats
    total_services = services.count()

    active_services = services.filter(
        is_active=True
    ).count()

    total_categories = services.values(
        'category'
    ).distinct().count()

    total_bookings = Booking.objects.filter(
        service__in=services
    ).count()

    stats = {
        'total_services': total_services,
        'active_services': active_services,
        'categories': total_categories,
        'total_bookings': total_bookings,
    }

    context = {
        "services": services,
        "stats": stats,
        "categories": categories,
    }

    return render(
        request,
        "dashboard/services.html",
        context
    )

@login_required
def staff_view(request):

    shops = Shop.objects.filter(owner=request.user)

    selected_shop_id = request.GET.get('shop', 'all')

    # =========================
    # STAFF QUERY
    # =========================

    if selected_shop_id == 'all':

        selected_shop = None

        staff_members = Staff.objects.filter(
            shop__owner=request.user
        )

    else:

        selected_shop = shops.filter(
            id=selected_shop_id
        ).first()

        staff_members = Staff.objects.filter(
            shop=selected_shop
        )

    staff_members = staff_members.select_related(
        'user',
        'shop'
    ).prefetch_related(
        'services'
    )

    # =========================
    # STATS
    # =========================

    total_staff = staff_members.count()

    available_now = staff_members.filter(
        accepts_bookings=True,
        is_active=True
    ).count()

    avg_rating = (
        staff_members.aggregate(
            avg=Avg('rating')
        )['avg'] or 0
    )

    total_appointments_today = Booking.objects.filter(
        staff__in=staff_members,
        date=timezone.now().date()
    ).count()

    stats = {
        'total_staff': total_staff,
        'available_now': available_now,
        'total_appointments_today': total_appointments_today,
        'avg_rating': round(avg_rating, 1),
    }

    context = {
        'staff_members': staff_members,
        'stats': stats,
        'shops': shops,
        'selected_shop_id': selected_shop_id,
    }

    return render(
        request,
        'dashboard/staff.html',
        context
    )

@login_required
def customers_view(request):

    shops = Shop.objects.filter(owner=request.user)

    selected_shop_id = request.GET.get("shop", "all")

    search = request.GET.get("search", "")

    bookings = Booking.objects.filter(
        shop__owner=request.user
    ).select_related(
        "customer",
        "service",
        "shop"
    )

    # =========================
    # SHOP FILTER
    # =========================

    if selected_shop_id != "all":
        bookings = bookings.filter(
            shop_id=selected_shop_id
        )

    # =========================
    # SEARCH FILTER
    # =========================

    if search:
        bookings = bookings.filter(
            customer__email__icontains=search
        )

    # =========================
    # UNIQUE CUSTOMERS
    # =========================

    customer_ids = bookings.values_list(
        "customer_id",
        flat=True
    ).distinct()

    customers = []

    for customer_id in customer_ids:

        customer_bookings = bookings.filter(
            customer_id=customer_id
        )

        # first_booking = customer_bookings.first()

        # customer = first_booking.customer

        first_booking = customer_bookings.first()

        if not first_booking:
          continue

        customer = first_booking.customer

        if not customer:
         continue

        total_bookings = customer_bookings.count()

        total_spent = customer_bookings.aggregate(
            total=Sum("price")
        )["total"] or 0

        favorite_service = (
            customer_bookings
            .values("service__name")
            .annotate(count=Count("id"))
            .order_by("-count")
            .first()
        )

        last_visit = (
            customer_bookings
            .order_by("-date")
            .first()
        )

        customers.append({

            "name": (
             customer.get_full_name()
             if customer and customer.get_full_name()
             else (customer.email if customer else "Unknown Customer")
            ),

           "email": customer.email if customer else "",
           "phone": customer.phone if customer else "",

            "avatar_initials": (
             customer.email[:2].upper()
             if customer.email
             else "CU"
            ),


            "total_bookings": total_bookings,

            'total_spent': round(total_spent, 0),

            "favorite_service": (
                favorite_service["service__name"]
                if favorite_service
                else "N/A"
            ),

            "last_visit": (
                last_visit.date
                if last_visit
                else None
            ),

            "status": (
                "vip"
                if total_spent >= 10000
                else "regular"
            ),

            "status_class": (
                "bg-yellow-100 text-yellow-700"
                if total_spent >= 10000
                else "bg-gray-100 text-gray-700"
            ),
        })

    # =========================
    # STATS
    # =========================

    total_customers = len(customers)

    vip_customers = len([
        c for c in customers
        if c["total_spent"] >= 10000
    ])

    current_month = timezone.now().month

    new_this_month = Booking.objects.filter(
        shop__owner=request.user,
        date__month=current_month
    ).values(
        "customer"
    ).distinct().count()

    total_revenue = bookings.aggregate(
        total=Sum("price")
    )["total"] or 0

    stats = {
        "total_customers": total_customers,
        "vip_customers": vip_customers,
        "new_this_month": new_this_month,
        "total_revenue": total_revenue,
    }

    context = {

        "customers": customers,

        "stats": stats,

        "shops": shops,

        "selected_shop_id": str(selected_shop_id),

        "search": search,
    }

    return render(
        request,
        "dashboard/customers.html",
        context
    )

@login_required
def reports_view(request):
    return render(request, "dashboard/reports.html")


def payment_success(request):

    plan = request.GET.get("plan")

    context = {
        "plan": plan
    }

    return render(request, 'dashboard/payment_success.html', context)


def payment_cancel(request):
    return render(request, 'dashboard/payment_cancel.html')


from django.shortcuts import render, redirect, get_object_or_404
from apps.services.forms import ServiceForm

@login_required
def service_edit(request, service_id):

    service = get_object_or_404(Service, id=service_id)

    if request.method == "POST":

        form = ServiceForm(
            request.POST,
            instance=service
        )

        if form.is_valid():
            form.save()

            return redirect(
                "dashboard:services"
            )

    else:
        # form = ServiceForm(
        #     instance=service
        # )
        if request.method == "POST":
          form = ServiceForm(
              request.POST, 
              instance=service, 
              shop=service.shop
            )
        else:
          form = ServiceForm(
              instance=service, 
              shop=service.shop
            )

    return render(
        request,
        "dashboard/service_edit.html",
        {
            "form": form,
            "service": service
        }
    )

def service_delete(request, service_id):

    service = get_object_or_404(Service, id=service_id)

    service.delete()

    return redirect('services')

@login_required
def service_add(request):
    return render(request, "dashboard/service_add.html")
 