from banal import ensure_dict
from furl import furl

from .util import get_value_from_xp as x


def get_paginated_url(context, data, url):
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
    handle:
        next_page: fetch
        store: store
    """
    if "pagination" in context.params:
        pagination = ensure_dict(context.params["pagination"])
        page = data.get("page", 1)
        if "total" in pagination and "per_page" in pagination:
            total = pagination["total"]
            per_page = pagination["per_page"]
            if isinstance(total, str):  # xpath
                total = int(x(html, total))
            if isinstance(per_page, str):  # xpath
                per_page = int(x(html, per_page))
            if page * per_page < total:
                context.log.info(f"Next page: {page + 1}")
                context.emit("next_page", data={**data, **{"page": page + 1}})
                return
