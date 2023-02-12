from django.contrib import admin

# Register your models here.
from django.contrib import admin
from eMarket.models import Category, Products, UserInfo, OrderItem, Order, Address, Payment
# Register your models here.

admin.site.register(Category)
admin.site.register(Products)
admin.site.register(UserInfo)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Address)
admin.site.register(Payment)
