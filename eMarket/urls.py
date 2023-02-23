from django.urls import path
from eMarket import views
from django.views.decorators.csrf import csrf_exempt

app_name = 'eMarket'


urlpatterns = [
    path('', views.homePage, name = 'home'),
    path('category/', views.categoryPage, name = 'category'),
    path('category-detail/<slug>/', views.categoryDetailPage, name = 'category-detail'),
    path('register-user/', views.registerUser, name='register-user'),
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
    path('payment-success/<ref_code>/', views.paymentSuccess, name = 'payment-success'),
    path('export-csv/', views.exportCSV, name = 'export-csv'),
    path('export-pdf/', views.exportPDF, name = 'export-pdf'),
    #path('export-excel/', views.exportExcel, name = 'export-excel'),
    path('contact/', views.contact, name = 'contact'),
    path('search/', csrf_exempt( views.searchProduct), name = 'search')
    
    
    #path('config/', views.stripe_config),
]
