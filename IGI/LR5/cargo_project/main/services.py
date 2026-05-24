"""External API clients and matplotlib chart generation."""
import base64
import io
import logging
from typing import Any, Dict

import requests
from django.conf import settings

logger = logging.getLogger('main')


def fetch_random_quote(timeout: float = 5.0) -> Dict[str, Any]:
    """Fetch a random motivational quote (quotable.io)."""
    try:
        resp = requests.get(settings.QUOTABLE_API, timeout=timeout, verify=False)
        resp.raise_for_status()
        data = resp.json()
        logger.info('Loaded quote from quotable')
        return {
            'content': data.get('content', ''),
            'author': data.get('author', 'Unknown'),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning('Quote API failed: %s', exc)
        return {
            'content': 'Дорогу осилит идущий.',
            'author': 'Народная мудрость',
        }


def fetch_currency_rates(timeout: float = 5.0) -> Dict[str, Any]:
    """USD-based currency rates (open.er-api.com)."""
    try:
        resp = requests.get(settings.EXCHANGE_API, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        rates = data.get('rates', {})
        logger.info('Loaded currency rates: %s codes', len(rates))
        return {
            'base': data.get('base_code', 'USD'),
            'updated': data.get('time_last_update_utc', ''),
            'rates': {
                code: rates.get(code) for code in ('BYN', 'EUR', 'RUB', 'PLN', 'USD')
                if code in rates
            },
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning('Currency API failed: %s', exc)
        return {
            'base': 'USD',
            'updated': '',
            'rates': {'USD': 1.0, 'EUR': 0.92, 'BYN': 3.27, 'RUB': 91.5, 'PLN': 4.05},
        }


def render_chart_png_base64(labels, values, title='', ylabel='') -> str:
    """Render a bar chart with matplotlib and return base64 PNG."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values, color='#3a7bd5')
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=30, ha='right')
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('ascii')
