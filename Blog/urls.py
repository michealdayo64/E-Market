from django.urls import path
from Blog import views

urlpatterns = [
    path('', views.blogList, name = 'blog'),
    path('blog_detail/<id>/', views.blogDetail, name = 'blog_detail'),

]