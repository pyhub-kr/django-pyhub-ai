from uuid import uuid4

from django import template

register = template.Library()


@register.simple_tag
def uuid4_hex(prefix="id_"):
    return (prefix or "") + uuid4().hex
