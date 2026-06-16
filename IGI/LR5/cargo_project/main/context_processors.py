"""Add globally-visible fields to every template context."""
import calendar
import time
from datetime import datetime, timezone as dt_timezone

from django.conf import settings

_RU_MONTHS = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
]
_RU_DAYS_SHORT = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']


def _build_calendar_data(year: int, month: int, today_day: int):
    """Return dict with month header and weeks list for template rendering."""
    weeks_raw = calendar.monthcalendar(year, month)
    weeks = []
    for week in weeks_raw:
        cells = []
        for d in week:
            cells.append({
                'day': d if d != 0 else None,
                'today': d == today_day,
            })
        weeks.append(cells)
    return {
        'month_name': _RU_MONTHS[month - 1],
        'year': year,
        'day_names': _RU_DAYS_SHORT,
        'weeks': weeks,
    }


def site_context(request):
    """Expose timezone info, current time and a calendar data dict to templates."""
    # Используем встроенные функции Python для получения таймзоны сервера
    now_utc = datetime.now(dt_timezone.utc)   # текущее время UTC
    now_local = datetime.now()                # локальное время сервера (naive — без tzinfo)
    server_tz = time.strftime('%Z')           # название таймзоны сервера ('UTC', 'MSK' и т.д.)

    calendar_data = _build_calendar_data(
        now_local.year, now_local.month, now_local.day
    )

    return {
        'site_company_name': getattr(settings, 'COMPANY_NAME', 'CargoGo'),
        'user_timezone': server_tz,
        'now_utc': now_utc,
        'now_local': now_local,
        'calendar_data': calendar_data,
    }
