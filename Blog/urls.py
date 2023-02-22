from django.urls import path
from Blog import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.blogList, name = 'blog'),
    path('blog_detail/<id>/', views.blogDetail, name = 'blog_detail'),
    path('blog-search/', csrf_exempt(views.searchBlog), name = 'blog-search')
]