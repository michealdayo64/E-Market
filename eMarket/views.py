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
from django.views.generic import View
from django.conf import settings
from rest_framework.authtoken.models import Token
import json
import secrets
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime
import csv
import xlwt
from usercontact.models import Contact
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile

# Create your views here.

import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY



def create_ref_code():
    ref = secrets.token_urlsafe(50)
    return ref




def registerUser(request):
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
    paginator = Paginator(products, 6)
    page_request_var = 'page'
    page_num = request.GET.get(page_request_var)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:   
        page_obj = paginator.page(paginator.num_pages) 
    print(page_obj)
    context = {
        'categories': categories,
        'products': products,
        'page_obj': page_obj,
        'disc_prices': disc_prices,
        'page_num': page_request_var
    }
    return render(request, 'eMarket/shop.html', context)

def categoryPage(request):
    categories = Category.objects.all().order_by('-created')
    context = {
        'categories': categories,
    }
    return render(request, 'eMarket/category.html', context)

def categoryDetailPage(request, slug):
    category = Category.objects.get(slug = slug)
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
        messages.info(request, "One Favourite Item Removed")
        return redirect("eMarket:fav_product")
        
    else:
        prod_id.favourite.add(request.user)
        messages.info(request, "One Favourite Item Added")
        return redirect("eMarket:fav_product")
        
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
        print(order)
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
            print(order_item)
            order_item.update(ordered = True)
            for item in order_item:
                item.save()

            #ASSIGN THE PAYMENT TO THE ORDER
            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()
            messages.success(self.request, "Your order was successful")
            return redirect("eMarket:payment-success", order.ref_code)
            #return paymentSuccess(order.ref_code)

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

def paymentSuccess(request, ref_code):
    order = Order.objects.get(user=request.user, ordered = True, ref_code = ref_code)
    return render(request, 'eMarket/payment_success.html', {'order': order})

def exportCSV(request):
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = f'attachment; filename=Reciept \ {datetime.datetime.now()}.csv'

    writer = csv.writer(response)
    writer.writerow(['title', 'description', 'quantity' 'price', 'Total'])

    order = Order.objects.get(user = request.user, ordered = True, export_csv = False)
    
    for ord in order.items.all():
        writer.writerow([ord.item.title, ord.item.description, ord.quantity, ord.get_final_price(), ''])
        
    writer.writerow(['','','','', order.get_total()])
    
    order.export_csv = True
    order.save()
    
    return response



def contact(request):
    if request.method == "POST":
        email = request.POST.get('email')
        message = request.POST.get('message')

        Contact.objects.create(email = email, message = message)
        messages.success(request, 'Message sent')
        return redirect('eMarket:contact')
    return render(request, 'eMarket/contact.html')

def exportPDF(request):
    response = HttpResponse(content_type = 'application/pdf')
    response['Content-Disposition'] = f'inline; attachment; filename=Reciept \ {datetime.datetime.now()}.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    order = Order.objects.filter(user = request.user)[0]
    ord = order.items.all()

    html_string = render_to_string('eMarket/pdf_output.html', {'reciept': ord, 'total': order.get_total()})
    html = HTML(string = html_string)
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())
     
    return response



'''def exportExcel(request):
    response = HttpResponse(content_type = 'application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename=Reciept \ {datetime.datetime.now()}.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Payment recieve')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold =True

    columns = ['title', 'description', 'quantity' 'price']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()

    order = Order.objects.get(user = request.user, ordered = True, export_excel = False)
    #ord = order.items.all().values_list('items_item_title', 'items_item_description', 'items_quantity' 'items_get_total_price')

    rows = []
    print(rows)
    for ord in order.items.all():
        data = {
            'title': ord.item.title,
            'description': ord.item.description,
            'quantity': ord.quantity,
            'price': ord.get_final_price()
        }
        rows.append(data)

    for row in rows:
        row_num=+1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    
    order.export_excel = True
    order.save()
    wb.save(response)
    return response'''








# JSON FOR SERRCH PRODUCT
def searchProduct(request):
    if request.method == 'POST':
        prod = json.loads(request.body)
        search = prod.get('search')

        search_prods = Products.objects.filter(title__icontains = search) | Products.objects.filter(description__icontains = search) | Products.objects.filter(category__slug__icontains = search)
        result = []
        if (search_prods):
            for i in search_prods:
                data = {
                    'title': i.title,
                    'description': i.description,
                    'img': i.image.url,
                    'price': i.price,
                    'prod_url': i.slug,
                    'auth': request.user.is_authenticated,
                    'id': i.id,
                    'fav': i.favourite
                }
                result.append(data)
            return JsonResponse(json.dumps(result, indent=4, sort_keys=True, default=str), safe=False)
        else:
            data = {
                'resErr': 'You can not send an empty data'
            }
            return JsonResponse(json.dumps(data, indent=4, sort_keys=True, default=str), safe=False)
        










       