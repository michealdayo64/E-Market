from django.shortcuts import render
from .models import Post, Comment
import json
from django.http import JsonResponse
# Create your views here.

def blogList(request):
    blog = Post.objects.all().order_by('-created')
    blog_thre = Post.objects.all().order_by('-created')[:3]
    return render(request, 'eMarket/blog.html', {'blog': blog, 'blog_thre': blog_thre})

def blogDetail(request, id):
    post_detail = Post.objects.get(id = id)
    blog_thre = Post.objects.all().order_by('-created')[:3]
    comment_list = Comment.objects.all()

    if request.method == 'POST':
        author = request.POST.get('author')
        email = request.POST.get('email')
        comment = request.POST.get('comment')

        Comment.objects.create(post = post_detail, author = author, email = email, comment = comment)
        
    return render(request, 'eMarket/blog_detail.html', {'post_detail': post_detail, 'blog_thre': blog_thre, 'comment_list': comment_list})


def searchBlog(request):
    if request.method == 'POST':
        prod = json.loads(request.body)
        search = prod.get('search')
        search_blogs = Post.objects.filter(title__icontains = search) | Post.objects.filter(description__icontains = search)
        result = []
        if (search_blogs):
            for i in search_blogs:
                data = {
                    'title': i.title,
                    'description': i.description,
                    'img': i.image.url,
                    'date': str(i.created),
                    'id': i.id
                }
                result.append(data)
            return JsonResponse(json.dumps(result, indent=4, sort_keys=True, default=str), safe=False)
        else:
            data = {
                'resErr': 'You can not send an empty data'
            }
            return JsonResponse(json.dumps(data, indent=4, sort_keys=True, default=str), safe=False)