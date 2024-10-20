from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from app.forms import CommentForm, SubscribeForm
from app.models import Comments, Post, Tag

# Create your views here.

def index(request):
    posts= Post.objects.all()
    top_posts= Post.objects.all().order_by('-view_count')[0:3] 
    recent_posts= Post.objects.all().order_by('-last_updated')[0:3]
    featured_blog= Post.objects.filter(is_featured=True)
    subscribe_form= SubscribeForm()
    subscribe_successful= None

    if featured_blog:
        featured_blog= featured_blog[0]

    if request.POST:
        subscribe_form= SubscribeForm(request.POST)
        if subscribe_form.is_valid():
            subscribe_form.save()
            subscribe_successful= 'Subscribed successfully'
            subscribe_form=SubscribeForm()

    context= {'posts': posts, 'top_posts': top_posts, 'recent_posts': recent_posts, 'subscribe_form':subscribe_form, 'subscribe_successful':subscribe_successful, 'featured_blog':featured_blog}
    return render(request, 'app/index.html', context)

def post_page(request, slug):
    post= Post.objects.get(slug=slug)
    comments= Comments.objects.filter(post=post, parent=None)
    form= CommentForm()

    if request.POST:
        comment_form= CommentForm(request.POST)
        if comment_form.is_valid():
            parent_obj= None
            if request.POST.get('parent'):
                parent= request.POST.get('parent')
                parent_obj= Comments.objects.get(id=parent)
                if parent_obj:
                    comment_reply= comment_form.save(commit=False)
                    comment_reply.parent= parent_obj
                    comment_reply.post= post
                    comment_reply.save()
                    return HttpResponseRedirect(reverse('post_page', kwargs={'slug':slug}))
            else:
                comment= comment_form.save(commit=False)
                postid= request.POST.get('post_id')
                post= Post.objects.get(id=postid)
                comment.post= post
                comment.save()
                return HttpResponseRedirect(reverse('post_page', kwargs={'slug':slug}))

    if post.view_count is None:
        post.view_count = 1
    else:
        post.view_count +=1
    post.save()
    context= {'post': post, 'form': form, 'comments': comments}
    return render(request, 'app/post.html', context)

def tag_page(request, slug):
    tag= Tag.objects.get(slug=slug)
    top_posts= Post.objects.filter(tags__in=[tag.id]).order_by('-view_count')[0:2]
    recent_posts= Post.objects.filter(tags__in=[tag.id]).order_by('-last_updated')[0:3]
    tags= Tag.objects.all()

    context= {'tag':tag, 'top_posts':top_posts, 'recent_posts':recent_posts, 'tags':tags}

    return render(request, 'app/tag.html', context)
