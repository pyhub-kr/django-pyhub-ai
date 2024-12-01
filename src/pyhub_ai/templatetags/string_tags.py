from django import template

register = template.Library()


@register.filter
def strip(value: str) -> str:
    return value.strip()
