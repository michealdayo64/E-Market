#from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from eMarket.models import Category, Products, OrderItem, Order, Payment, Address, UserInfo
from eMarketApi.serializers import ( CategorySerializer, ProductSerializer, UserSerializer, PaymentSerializer,
        UserInfoSerializer, OrderItemSerializer, OrderSerializer, AddressSerializer )
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from rest_framework import permissions
from eMarketApi.permissions import IsOwnerOrReadOnly
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
#from django.contrib.auth.decorators import login_required


# Create your views here.

class UserList(generics.ListAPIView):
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        #permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
        )
    '''def perform_create(self, serializer):
        serializer.save(owner = self.request.user)'''

class UserCreate(APIView):
    def post(self, request):
        user_list = UserSerializer(data = request.data)
        phone_no = request.data['phone_no']
        address = request.data['address']
        if user_list.is_valid():
            user = user_list.save()
            user.set_password(user.password)
            user.save()
            Token.objects.create(user = user)
            UserInfo.objects.create(
                user = user,
                phone_no = phone_no,
                address = address
            )
        data = {
            "user_list": user_list.data,   
            }  
        return Response(data)

class UserInfoList(APIView):
    def get(self, request):
        user = UserInfo.objects.all()
        serializer = UserInfoSerializer(user, many = True)
        return Response(serializer.data)

class UserInfoDetail(APIView):
    def get(self, request, pk):
        user = UserInfo.objects.get(pk = pk)
        serializer = UserInfoSerializer(user)
        return Response(serializer.data)

class LoginView(APIView):
    #permission_classes = (IsAuthenticated, )
    def post(self, request,):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                data = {
                    "token": user.auth_token.key, 
                    'success': 'Login Successfully'}
                return Response(data = data, status = status.HTTP_200_OK)
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
            logout(request)
            data = {'success': 'success loggout'}
            return Response(data = data, status = status.HTTP_200_OK)

class CategoryList(APIView):
    def get(self, request):
        cat = Category.objects.all()
        serializer = CategorySerializer(cat, many = True)
        #print(serializer)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.error)

class CategoryDetail(APIView):
    def get(self, request, pk):
        catD = get_object_or_404(Category, pk = pk)
        data = CategorySerializer(catD).data
        print(data)
        return Response(data)   


class ProductList(APIView):
    def get(self, request):
        prod = Products.objects.all()
        serializer = ProductSerializer(prod, many = True)
        print(serializer)
        return Response(serializer.data)
        

class ProductDetail(APIView):
    def get(self, request, pk):
        catD = get_object_or_404(Products, pk = pk)
        serializer = ProductSerializer(catD)
        print(serializer)
        return Response(serializer.data)


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def addToCartApi(request, id):
    item = get_object_or_404(Products, id=id)
    #USER CREATE ORDER ITEM
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)

    #CHECK IF USER HAS AN ORDER
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        #CHECK IF ORDER_ITEM IS IN THE ORDER
        if order.items.filter(item__id = item.id).exists():
            order_item.quantity += 1
        
            order_item.save()
            data = {
                'success': "This Item quantiry was updated"
            }
            return Response(data = data)
        else:      
            order.items.add(order_item)
            
            data = {
                "success": "This item was added to your cart"
            }
            return Response(data = data)

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        
        data = {
                "success": "This item was added to your cart"
            }
        return Response(data = data)
    return Response(item.data)


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def removeFromCartApi(request, id):
    item = get_object_or_404(Products, id=id, available = True)
    #CHECK IF USER HAS AN ORDER
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]

    #CHECK IF ORDER_ITEM IS IN THE ORDER
        if order.items.filter(item__id = item.id).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            
            data = {
                "success": "This item was remove from your cart"
            }
            return Response(data = data)
        else:
            data = {
                "success": "This item was not in your cart"
            }
            return Response(data = data)
    else:
        data = {
                "success": "You do not have an active order"
            }
        return Response(data = data)
    return Responset(data = data)


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def removeSingleItemFromCartApi(request, id):
    item = get_object_or_404(Products, id = id, available = True)
    #CHECK IF USER HAS AN ORDER
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]

    #CHECK IF ORDER_ITEM IS IN THE ORDER
        if order.items.filter(item__id = item.id).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.item.stock += 1
                order_item.save()
            else:
                order.items.remove(order_item)
            data = {
                'success': 'This item quantity was Updated'
            }
            return Response(data = data)
        else:
            data = {
                'success': 'This item was not in your cart'
            }
            return Response(data = data)
    else:
        data = {
                'success': 'You do not have an active order'
            }
        return Response(data = data)

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def orderItemApi(request):
    try:
        item = Products.objects.all()
        order = OrderItem.objects.filter(user = request.user, item = item, ordered = False)
        cartItem = OrderItemSerializer(order)
        return Response(cartItem.data)
    except OrderItem.DoesNotExist:
        return Response(status = status.HTTP_404_NOT_FOUND)


class OrderItemList(generics.ListAPIView):  
    #queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        #permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
        )
    def perform_create(self, serializer):
        serializer.save(owner = self.request.user)

    def get_queryset(self):
        user = self.request.user
        return OrderItem.objects.filter(user = user)

class OrderItemDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        #permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    )
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class OrderList(generics.ListAPIView):
    
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        #permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
        )
    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user = user)

class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        #permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    )
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class AddressApi(generics.ListAPIView):
    
    queryset = Address.objects.all()
    #print(queryset)
    serializer_class = AddressSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        #permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
        )

    def get_queryset(self):
        user = self.request.user
        return Address.objects.filter(user = user)

class PaymentApi(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwnerOrReadOnly,
    )
    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(user = user)



    






