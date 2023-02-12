from django import template
from eMarket.models import Order, Products

register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].total_quantity()
    return 0

@register.filter
def product_price(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].get_total()
    return 0

@register.filter
def favourite_item_count(user):
    if user.is_authenticated:
        qs = Products.objects.filter(favourite = user)
        if qs.exists():
            return qs[0].favourite.count()
    return 0