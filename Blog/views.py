from django.shortcuts import render
from .models import Post
# Create your views here.

def blogList(request):
    blog = Post.objects.all()
    return render(request, 'eMarket/blog.html', {'blog': blog})

def blogDetail(request, id):
    post_detail = Post.objects.get(id = id)
    return render(request, 'eMarket/blog_detail.html', {'post_detail': post_detail})
