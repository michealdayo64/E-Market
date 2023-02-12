from rest_framework import serializers
from eMarket.models import UserInfo, Category, Products, OrderItem, Order, Address, Payment
from django.contrib.auth.models import User
#from rest_framework.models import Token
from rest_framework.authtoken.models import Token



class UserInfoSerializer(serializers.ModelSerializer):
    #user = serializers.SlugRelatedField(queryset = User.objects.all(), slug_field = 'slug')
    class Meta:
        model = UserInfo
        fields = (
            'pk',
            #'user',
            'phone_no', 
            'address',
            #'slug',
            )

class UserSerializer(serializers.ModelSerializer):
    #products = OrderItemSerializer(many = True, read_only = True)
    user_profile = UserInfoSerializer(many = True, read_only = True)
    user = Token.objects.all()
    class Meta:
        #model = UserInfo
        model = User
        fields = (
            'pk',
            'username',
            'email',
            'password',
            'user_profile',
            'auth_token'
        )
        extra_kwargs = {'password': {'write_only': True}}

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    #category = serializers.SlugRelatedField(queryset = Category.objects.all(), slug_field = 'slug')
    #products = serializers.HyperlinkedRelatedField(many = True, read_only = True, view_name = 'eMarketApi:products-detail')
    #products = OrderItemSerializer(many = True, read_only = True)
    
    class Meta:
        model = Products
        fields = (
            'pk',
            #'category',
            'title',
            'discount_price',
            'slug',
            'description',
            'image',
            'price',
            'stock',
            'available',
            'created_date',
            'size',
            #'products',
            
            )

class CategorySerializer(serializers.ModelSerializer):
    categories = ProductSerializer(many = True, read_only = True)

    #products = ProductSerializer(many = True, read_only = True)
    #categories = serializers.PrimaryKeyRelatedField(many = True, read_only = True)

    class Meta:
        model = Category
        fields = ['pk','name','slug','created', 'photo', 'categories']



class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    #payment = OrderSerializer(many = True, read_only = True)
    class Meta:
        model = Payment
        fields = (
            'stripe_charge_id',
            'amount',
            'timestamp',
            #'payment',
        )

class AddressSerializer(serializers.HyperlinkedModelSerializer):
    #billing_address = OrderSerializer(many = True, read_only = True)
    class Meta:
        model = Address
        fields = (
            'first_name',
            'last_name',
            'country',
            'street_address',
            'apartment_address',
            'city',
            'zip_code',
            'order_note',
            'address_type',
            'default',
            #'billing_address',
        )

class OrderItemSerializer(serializers.HyperlinkedModelSerializer):
    item = serializers.SlugRelatedField(queryset = Products.objects.all(), slug_field = 'slug')
    #owner = serializers.ReadOnlyField(source = 'user.username')
    #user_order = OrderSerializer(many = True, read_only = True)

    class Meta:
        model = OrderItem
        fields = (
            'pk',
            'item',
            'quantity',
            'ordered',
            #'user_order',
           
        )

class OrderSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source = 'user.username')
    #billing_address = AddressSerializer(many = True, read_only = True)
    #items = OrderItemSerializer(many = True, read_only = True)
    #payment = PaymentSerializer(many = True, read_only = True)
    class Meta:
        model = Order
        fields = (
            'ref_code',
            'ordered',
            'being_delivered',
            'ordered_date',   
            'owner',
            #'billing_address',
            #'items',
            #'payment'
            
        )








    

