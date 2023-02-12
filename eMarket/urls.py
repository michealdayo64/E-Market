from django.urls import path
from eMarket import views

app_name = 'eMarket'


urlpatterns = [
    path('', views.homePage, name = 'home'),
    path('category/', views.categoryPage, name = 'category'),
    path('category-detail/<id>/', views.categoryDetailPage, name = 'category-detail'),
    path('register-user/', views.RegisterUser, name='register-user'),
    path('user-login/', views.userLogin, name='user-login'),
    path('user-logout/', views.userLogout, name = 'user-logout'),
    path('shop/', views.shopPage, name = 'shop'),
    path('product/<slug>/', views.productDetail, name = "detail"),
    path('favourite/<id>/', views.favourite, name = 'favourite'),
    path('fav_product/', views.favouriteProducts, name = 'fav_product'),
    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('remove/<slug>/', views.remove_from_cart, name = 'remove-from-cart'),
    path('reduce/<slug>/', views.remove_single_item_from_cart, name = 'reduce-from-cart'),
    path('order-summary/', views.OrderSummary.as_view(), name = 'order-summary'),
    path('checkout/', views.Checkout.as_view(), name = 'checkout'),
    path('payment/<paymentOption>/', views.PaymentView.as_view(), name = 'payment'),
    
    
    #path('config/', views.stripe_config),
]
