class PlanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        plan = request.GET.get('plan')

        # Agar URL me plan hai → session me save karo
        if plan:
            request.session['plan'] = plan

        # Har request me plan available rahe
        request.plan = request.session.get('plan')

        response = get_response(request)
        return response