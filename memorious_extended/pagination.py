from banal import ensure_dict
from furl import furl

from .util import get_value_from_xp as x
from .util import re_first


def _get_x_int(html, value):
    if isinstance(value, str):  # xpath
        value = x(html, value)
        value = re_first(r"\d+", value)
    return int(value)


def get_paginated_url(context, data, url=None):
    url = url or data.get("url")
    if url is None:
        return
    if "pagination" in context.params:
        pagination = ensure_dict(context.params["pagination"])
        if "param" in pagination:
            page = data.get("page", 1)
            f = furl(url)
            f.args[pagination["param"]] = page
            return f.url
    return url


def paginate(context, data, html):
    """
    as part in the html parse stages, look for next pages and emit them

    params:
        pagination:
            total:    # xpath to value or direct int value
            per_page: # xpath to value or direct int value
            param:    # name of url get param to manipulate page
    handle:
        next_page: fetch
        store: store
    """
    if "pagination" in context.params:
        pagination = ensure_dict(context.params["pagination"])
        page = data.get("page", 1)
        should_emit = False

        if "total" in pagination and "per_page" in pagination:
            total = _get_x_int(html, pagination["total"])
            per_page = _get_x_int(html, pagination["per_page"])
            if page * per_page < total:
                should_emit = True

        if "total_pages" in pagination:
            total_pages = _get_x_int(html, pagination["total_pages"])
            if page < total_pages:
                should_emit = True

        if should_emit:
            context.log.info(f"Next page: {page + 1}")
            data = {**data, **{"page": page + 1}}
            data["url"] = get_paginated_url(context, data)
            context.emit("next_page", data=data)
