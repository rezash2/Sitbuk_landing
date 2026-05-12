from urllib.parse import urlencode

from django import template

register = template.Library()


@register.filter
def at(items, index):
    try:
        return items[int(index)]
    except Exception:
        return ''


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    request = context.get('request')
    if not request:
        return ''
    query = request.GET.copy()
    for key, value in kwargs.items():
        if value in (None, ''):
            query.pop(key, None)
        else:
            query[key] = value
    encoded = query.urlencode()
    return f'?{encoded}' if encoded else ''
