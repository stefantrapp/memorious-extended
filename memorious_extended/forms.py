def get_form(context, html, xpath):
    """
    return (action, data) of the form in xpath
    """
    form = html.find(xpath)
    if form is None:
        context.log.error(f"Cannot find form: `{xpath}`")
        context.crawler.cancel()
        return None, None
    return form.xpath("@action")[0], {
        **{i.name: i.value for i in form.findall(".//input")},
        **{i.name: i.value for i in form.findall(".//select")},
    }
