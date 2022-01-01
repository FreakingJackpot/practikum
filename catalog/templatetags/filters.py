from django import template

register = template.Library()


@register.filter
def decimalspace(val_orig):
    val_new = f'{val_orig:,.2f}'.replace(',', ' ')
    print(val_new)
    return val_new
