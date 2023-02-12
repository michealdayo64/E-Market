from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

SIZE_CHOICES = (
    ('S', 'SMALL'),
    ('M', 'MEDIUM'),
    ('L', 'LARGE'),
    ('E', 'EXTRALARGE'),
)

ADDRESS_CHOICES = (
    ('B', 'billing'),
    ('S', 'shipping')
)

class UserInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'user_profile')
    phone_no = models.CharField(max_length = 12)
    address = models.CharField(max_length=200)
    

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length = 50, unique = True)
    created = models.DateTimeField(default = timezone.now)
    slug = models.SlugField()
    photo = models.ImageField(upload_to='media', default = False, blank = True)

    def __str__(self):
        return self.name

    @property
    def photo_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url


    def get_absolute_url(self):
        return reverse('eMarket:product_list_by_category', args=[self.slug])

class Products(models.Model):
    category = models.ForeignKey(Category, on_delete = models.CASCADE, related_name = 'categories')
    title = models.CharField(max_length=50, unique = True)
    discount_price = models.FloatField()
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to='media')
    price = models.FloatField()
    stock = models.PositiveIntegerField(default = False)
    available = models.BooleanField(default=True)
    created_date = models.DateTimeField(default = timezone.now)
    size = models.CharField(choices=SIZE_CHOICES, max_length=20, default = False)
    favourite = models.ManyToManyField(User, default = False, blank = True)

    def __str__(self):
        return self.title

    '''def favCount(self):
        total = 0
        for fav in self.favourite.all():
            total += fav.user.id
        return total'''

    def percent_removed(self):
        if self.price:
            return (20/100) * self.price

    def get_absolute_url(self):
        return reverse("eMarket:detail", kwargs={ 'slug' : self.slug })

    def get_add_to_cart_url(self):
        return reverse("eMarket:add-to-cart", kwargs={ 'slug' : self.slug })

    

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'users')
    item = models.ForeignKey(Products, on_delete=models.CASCADE, related_name = 'products')
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    

    def get_total_price(self):
        return self.quantity * self.item.price

    def get_total_discount_price(self):
        return self.quantity * self.item.discount_price
    
    def get_saved_price(self):
        return self.get_total_price() - self.get_total_discount_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        return self.get_total_price()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)   
    items = models.ManyToManyField(OrderItem, related_name = 'user_order')
    ref_code = models.CharField(max_length=20, default = False)
    ordered = models.BooleanField(default=False)
    being_delivered = models.BooleanField(default=False)
    ordered_date = models.DateField()
    #shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey('Address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    def total_quantity(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.quantity
        return total

    

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    country = models.CharField(max_length = 50)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    city = models.CharField(max_length = 100)
    zip_code = models.CharField(max_length=100)
    order_note = models.CharField(max_length = 100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    
    def __str__(self):
        return self.street_address

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username