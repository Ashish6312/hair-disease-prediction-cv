from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
import time


class TokenAuthFallbackMiddleware:
    """
    The static frontend (a different origin from this API) authenticates
    with the session cookie set at login. Some mobile browsers — Chrome on
    Android in particular — block that cross-site cookie outright, so the
    session never comes back on later requests even though login succeeded.

    As a fallback, api_login/api_register also hand back the session key as
    a bearer token. The frontend stores it and replays it as
    `Authorization: Bearer <token>` when it has one. Map that header onto the
    session cookie before SessionMiddleware runs, so the rest of the request
    is authenticated exactly as if the cookie had arrived normally.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cookie_name = settings.SESSION_COOKIE_NAME
        if cookie_name not in request.COOKIES:
            auth = request.META.get('HTTP_AUTHORIZATION', '')
            if auth.startswith('Bearer '):
                token = auth[len('Bearer '):].strip()
                if token:
                    request.COOKIES[cookie_name] = token
        return self.get_response(request)


class SessionTimeoutMiddleware:
    """
    Middleware to handle 30-minute session timeout
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Get last activity time from session
            last_activity = request.session.get('last_activity')
            current_time = time.time()
            
            # If this is the first request, set last activity
            if last_activity is None:
                request.session['last_activity'] = current_time
            else:
                # Check if session has expired (30 minutes = 1800 seconds)
                if current_time - last_activity > 1800:
                    # Session expired, logout user
                    logout(request)
                    messages.warning(request, 'Your session has expired. Please log in again.')
                    # Redirect to login page
                    return redirect('login')
                else:
                    # Update last activity time
                    request.session['last_activity'] = current_time

        response = self.get_response(request)
        return response
