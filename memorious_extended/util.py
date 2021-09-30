import re
from datetime import date, datetime

from dateparser import parse as dateparse2  # FIXME
from dateutil.parser import parse as dateparse
from jinja2 import BaseLoader, Environment
from servicelayer import env

from .exceptions import RegexError


def generate_url(template, data):
    """
    replace url string template (jinja syntax) with values from data
    """
    tmpl = Environment(loader=BaseLoader).from_string(template)
    return tmpl.render(**data)


def get_value_from_xp(html, path):
    """
    shorthand
    """
    part = html.xpath(path)
    if isinstance(part, list) and len(part) == 1:
        part = part[0]
    if hasattr(part, "text"):
        part = part.text
    if isinstance(part, str):
        return part.strip()
    return part


def ensure_date(value, **parserkwargs):
    if value is None:
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    value = str(value)
    try:
        do_raise = parserkwargs.pop("raise_on_error", False)
        return dateparse(value, **parserkwargs).date()
    except Exception:  # FIXME
        try:
            return dateparse2(value, **parserkwargs).date()
        except Exception as e:
            if do_raise:
                raise e
            return None


def cast(value, with_date=False, **dateparserkwargs):
    if not isinstance(value, (str, float, int)):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:  # ''
            return None
    try:
        if float(value) == int(float(value)):
            return int(value)
        return float(value)
    except (TypeError, ValueError):
        if with_date:
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                try:
                    return ensure_date(value, raise_on_error=True, **dateparserkwargs)
                except Exception:  # FIXME
                    pass
        # value = as_bool(value, None)
        return value


def casted_dict(d, ignore_keys=[], **dateparserkwargs):
    return {
        k: cast(v, with_date=True, **dateparserkwargs) if k not in ignore_keys else v
        for k, v in d.items()
    }


def re_first(pattern, string):
    try:
        value = re.findall(pattern, string)[0]
        return value.strip()
    except Exception as e:
        raise RegexError(str(e), string)


def get_env_or_context(context, key, default=None):
    return env.get(key) or context.params.get(key.lower(), default)
