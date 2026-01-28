from django.utils import timezone
from django.conf import settings

class SessionIdleTimeout:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_time = timezone.now()
            last_activity = request.session.get('last_activity')

            if last_activity:
                elapsed = (current_time - timezone.datetime.fromisoformat(last_activity)).total_seconds()
                if elapsed > settings.IDLE_TIMEOUT:
                    # Logout automatically
                    from django.contrib.auth import logout
                    logout(request)
                    request.session.flush()

            # Update last activity
            request.session['last_activity'] = current_time.isoformat()

        return self.get_response(request)
