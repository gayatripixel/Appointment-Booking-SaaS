from django.shortcuts import render
from django.conf import settings


def pricing_view(request):

    context = {
        "razorpay_key": settings.RAZORPAY_KEY_ID
    }

    return render(
        request,
        "subscriptions/pricing.html",
        context
    )