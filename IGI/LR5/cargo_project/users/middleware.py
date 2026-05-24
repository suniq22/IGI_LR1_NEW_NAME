"""Activate the user's preferred timezone on each request."""
import logging

import pytz
from django.utils import timezone

logger = logging.getLogger('users')


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = None
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            profile = getattr(user, 'profile', None)
            if profile and profile.timezone:
                tzname = profile.timezone
        if not tzname:
            tzname = request.session.get('django_timezone')
        if tzname:
            try:
                timezone.activate(pytz.timezone(tzname))
            except Exception as exc:  # noqa: BLE001
                logger.warning('Bad timezone %s: %s', tzname, exc)
                timezone.deactivate()
        else:
            timezone.deactivate()
        return self.get_response(request)
