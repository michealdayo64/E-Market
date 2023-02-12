from django.shortcuts import render, get_object_or_404, redirect
from eMarket.models import Category, Products, OrderItem, Order, Address, Payment
from Blog.models import Post
from eMarket.forms import UserForm, UserInfoForm, CheckoutForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.contrib import messages
from django.views.generic import ListView, DetailView, View
from django.conf import settings
from rest_framework.authtoken.models import Token

# Create your views here.

import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits))


def RegisterUser(request):
    user_form = UserForm(request.POST or None)
    userInfo_form = UserInfoForm(request.POST or None)
    if user_form.is_valid() and userInfo_form.is_valid():
        user = user_form.save()
        user.set_password(user.password)
        user.save()

        profile_info = userInfo_form.save(commit = False)
        profile_info.user = user
        profile_info.save()
        Token.objects.create(user = user)

    else:
        messages.info(request, userInfo_form.errors)
        print(user_form.errors, userInfo_form.errors)
    user_form = UserForm()
    userInfo_form = UserInfoForm()

    context = {
        'user_form' : user_form,
        'userInfo_form' : userInfo_form
    }
    return render(request, 'eMarket/signup.html', context)

def userLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request,user)
                messages.info(request, "Login Successfully")
                return redirect("eMarket:home")               
            
        else:
            print("Someone tried to login and failed")
            print("username:{} and password:{}".format(username,password))
            messages.info(request, "Invalid Details")
            return redirect("eMarket:user-login")
    else:
        return render(request, 'eMarket/login.html')

@login_required
def userLogout(request):
    logout(request)
    return redirect("/")

def homePage(request, category_slug = None):
    category = False
    categories = Category.objects.all().order_by('-created')
    products = Products.objects.filter(available = True)
    posts = Post.objects.all().order_by('created')[:3]
    
    if category_slug:
        category = get_object_or_404(Category, slug = category_slug)
        products = products.filter(category = category)
        
    context = {
        'categories': categories,
        'products': products,
        'category': category,
        'posts': posts
    }
    #print(products)
    return render(request, 'eMarket/index.html', context)

def shopPage(request):
    categories = Category.objects.all().order_by('-created')
    products = Products.objects.filter(available = True)
    disc_prices = Products.objects.filter(discount_price__gt = 0)
    context = {
        'categories': categories,
        'products': products,
        'disc_prices': disc_prices
    }
    return render(request, 'eMarket/shop.html', context)

def categoryPage(request):
    categories = Category.objects.all().order_by('-created')
    context = {
        'categories': categories,
    }
    return render(request, 'eMarket/category.html', context)

def categoryDetailPage(request, id):
    category = Category.objects.get(id = id)
    categories = Category.objects.all().order_by('-created')
    products = products = Products.objects.filter(available = True, category = category)
    context = {
        'category': category,
        'categories': categories,
        'products': products
                }
    return render(request, 'eMarket/catdetail.html', context)

def productDetail(request, slug):
    #product = Products.objects.get()
    product = get_object_or_404(Products, slug=slug, available=True)

    context = {
        'prod': product,
    }
    return render(request, 'eMarket/shop_detail.html', context)

@login_required
def favourite(request, id):
    prod_id = get_object_or_404(Products, id = id, available=True)
    if prod_id.favourite.filter(id = request.user.id).exists():
        prod_id.favourite.remove(request.user)
        return redirect("eMarket:fav_product")
        messages.info(request, "One Favourite Item Removed")
    else:
        prod_id.favourite.add(request.user)
        return redirect("eMarket:fav_product")
        messages.info(request, "One Favourite Item Added")
    return redirect("eMarket:detail", id = id)

def favouriteProducts(request):
    #product = Products.objects.all()
    fav_prod = Products.objects.filter(favourite = request.user)
    categories = Category.objects.all().order_by('-created')
    context = {
        'fav_prod': fav_prod,
        'categories': categories,
    }
    return render(request, 'eMarket/favourite_product.html', context)
    

@login_required
def add_to_cart(request, slug):
    try:
        item = get_object_or_404(Products, slug=slug, available = True)

        #USER CREATE ORDER ITEM
        order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)

        #CHECK IF USER HAS AN ORDER
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]

        #CHECK IF ORDER_ITEM IS IN THE ORDER
            if order.items.filter(item__slug = item.slug).exists():
                #order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
                order_item.quantity += 1
                order_item.item.stock -= 1
                order_item.save()
                messages.info(request, "This Item quantity was updated")
                return redirect("eMarket:order-summary")
            else:      
                order.items.add(order_item)
                messages.info(request, "This item was added to your cart")
                return redirect("eMarket:order-summary")
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart")
            return redirect("eMarket:order-summary")
        return redirect("eMarket:detail", slug=slug)
    except ObjectDoesNotExist:
        messages.errors(request, "no product availaible")
        return redirect('/')



@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Products, slug=slug, available = True)
    #CHECK IF USER HAS AN ORDER
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]

    #CHECK IF ORDER_ITEM IS IN THE ORDER
        if order.items.filter(item__slug = item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request, "This item was remove from your cart")
            return redirect("eMarket:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("eMarket:order-summary")

    else:
        messages.info(request, "You do not have an active order")
        return redirect("eMarket:order-summary")
    return redirect("eMarket:order-summary")


@login_required
def remove_single_item_from_cart(request, slug):

    item = get_object_or_404(Products, slug=slug, available = True)
    #CHECK IF USER HAS AN ORDER
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]

    #CHECK IF ORDER_ITEM IS IN THE ORDER
        if order.items.filter(item__slug = item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.item.stock += 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was Updated")
            return redirect("eMarket:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("eMarket:order-summary")

    else:
        messages.info(request, "You do not have an active order")
        return redirect("eMarket:order-summary")



class OrderSummary(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object' : order
            }
            return render(self.request, "eMarket/order_summary.html", context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active Order")
            return redirect("/") 

class Checkout(View):
    def get(self, *args, **kwargs):
        try:
            form = CheckoutForm()
            order = get_object_or_404(Order, user = self.request.user, ordered = False)
            order.save()

            context = {
                'order': order,
                'form': form
            }
            
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("eMarket:checkout")
        return render(self.request, "eMarket/checkout.html", context)
        
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = get_object_or_404(Order, user = self.request.user, ordered = False)
            
            if form.is_valid():
                firstName = form.cleaned_data.get('first_name')
                lastName = form.cleaned_data.get('last_name')
                country = form.cleaned_data.get('country')
                streetAddress = form.cleaned_data.get('street_address')
                apartmentAddress = form.cleaned_data.get('apartment_address')
                city = form.cleaned_data.get('city')
                zip_code = form.cleaned_data.get('zip')
                orderNote = form.cleaned_data.get('order_note')
                paymentOption = form.cleaned_data.get('payment_option')
                billingAddress = Address(
                    user = self.request.user,
                    first_name = firstName,
                    last_name = lastName,
                    country = country,
                    street_address = streetAddress,
                    apartment_address = apartmentAddress,
                    city = city,
                    zip_code = str(zip_code),
                    order_note = orderNote,
                    address_type = 'B'
                )
                billingAddress.save()
                order.billing_address = billingAddress
                order.save()

                #TODO add redirect to the selected payment option
                if paymentOption == 'S':
                    return redirect("eMarket:payment", paymentOption='stripe')
                elif paymentOption == 'P':
                    return redirect("eMarket:payment", paymentOption='stripe')
                else:
                    messages.warning(self.request, "Invalid details")
                    return redirect("eMarket:checkout")

                return redirect("eMarket:checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active Order")
            return redirect("eMarket:summary")




class PaymentView(View):
    def get(self, *args, **kwargs):
        key = settings.STRIPE_PUBLISHABLE_KEY
        order = Order.objects.get(user=self.request.user, ordered = False)
        if order.billing_address:
            context = {
                'order' : order,
                'DISPLAY_COUPON_FORM' : False,
                'key': key
            }
            return render(self.request, 'eMarket/payment.html', context)
        else:
            messages.warning(self.request, "You do not have a billing_address yet")
            return redirect("eMarket:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered = False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)
        
        
        try:
            charge = stripe.Charge.create(
                amount = amount, #Amount in cents
                currency = "usd",
                source = token, #obtained with Stripe.js
            )

            #CREATE PAYMENT
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order_item = order.items.all()
            order_item.update(ordered = True)
            for item in order_item:
                item.save()

            #ASSIGN THE PAYMENT TO THE ORDER
            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()
            messages.success(self.request, "Your order was successful")
            return redirect('eMarket:home')

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("eMarket:home")
            
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit error")
            return redirect("eMarket:home")
            
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's APi
            messages.error(self.request, "Invalid parameters")
            return redirect("eMarket:home")
            
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Authentication failed")
            return redirect("eMarket:home")
            
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network Failed")
            return redirect("eMarket:home")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Something went wrong. You were not charged")
            return redirect("eMarket:home")
            
        except Exception as e:
            # Send email to ourselves
            messages.error(self.request, "serious error occured, we have been notified")
            return redirect("eMarket:home")









       