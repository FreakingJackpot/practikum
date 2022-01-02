from django import template

register = template.Library()


@register.filter
def decimalspace(val_orig):
    val_new = f'{val_orig:,.0f}'.replace(',', ' ')
    return val_new
