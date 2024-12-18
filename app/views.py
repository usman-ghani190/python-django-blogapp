from turtle import title
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

from app.forms import CommentForm, NewUserForm, SubscribeForm
from app.models import Comments, Post, Profile, Tag, WebsiteMeta

from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db.models import Count

# Create your views here.

def index(request):
    posts= Post.objects.all()
    top_posts= Post.objects.all().order_by('-view_count')[0:3] 
    recent_posts= Post.objects.all().order_by('-last_updated')[0:3]
    featured_blog= Post.objects.filter(is_featured=True)
    subscribe_form= SubscribeForm()
    subscribe_successful= None
    website_info= None

    if WebsiteMeta.objects.all().exists():
        website_info= WebsiteMeta.objects.all()[0]

    if featured_blog:
        featured_blog= featured_blog[0]

    if request.POST:
        subscribe_form= SubscribeForm(request.POST)
        if subscribe_form.is_valid():
            subscribe_form.save()
            request.session['subscribed']= True
            subscribe_successful= 'Subscribed successfully'
            subscribe_form=SubscribeForm()

    context= {'posts': posts, 'top_posts': top_posts, 'recent_posts': recent_posts, 'subscribe_form':subscribe_form, 'subscribe_successful':subscribe_successful, 'featured_blog':featured_blog, 'website_info':website_info}
    return render(request, 'app/index.html', context)

def post_page(request, slug):
    post= Post.objects.get(slug=slug)
    comments= Comments.objects.filter(post=post, parent=None)
    form= CommentForm()

    # Bookmark
    bookmark=False
    if post.bookmarks.filter(id= request.user.id).exists():
        bookmark=True
    is_bookmarked=bookmark

    # Likes
    like=False
    if post.like.filter(id= request.user.id).exists():
        like=True
    is_liked= like

    # show_comments=None
    # comments
    # post = get_object_or_404(Post, slug=slug)
    # show_comments = post.comments.filter(parent=None).exists()
    # show_comments= False
    # if post.comments.filter(parent=None):
    #     show_comments= True
    
    # comments = post.comments.filter(parent=None)if show_comments else []
    # form = CommentForm()

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

    recent_posts= Post.objects.exclude(id= post.id).order_by('-last_updated')[0:3]
    top_authors= User.objects.annotate(number= Count('post')).order_by('-number')[0:3]
    tags= Tag.objects.all()
    related_posts= Post.objects.exclude(id= post.id).filter(author= post.author)[0:2]


    context= {'post': post,
               'form': form, 
               'comments': comments, 
               'is_bookmarked':is_bookmarked, 
               'is_liked':is_liked,
               'recent_posts':recent_posts,
               'top_authors':top_authors,
               'tags':tags,
               'related_posts':related_posts,
            #    'show_comments':show_comments
                }
    return render(request, 'app/post.html', context)

def tag_page(request, slug):
    tag= Tag.objects.get(slug=slug)
    top_posts= Post.objects.filter(tags__in=[tag.id]).order_by('-view_count')[0:2]
    recent_posts= Post.objects.filter(tags__in=[tag.id]).order_by('-last_updated')[0:3]
    tags= Tag.objects.all()

    context= {'tag':tag, 'top_posts':top_posts, 'recent_posts':recent_posts, 'tags':tags}

    return render(request, 'app/tag.html', context)

def author_page(request, slug):
    profile= Profile.objects.get(slug=slug)

    top_posts= Post.objects.filter(author= profile.user).order_by('-view_count')[0:2]
    recent_posts= Post.objects.filter(author= profile.user).order_by('-last_updated')[0:3]
    top_authors=User.objects.annotate(number= Count('post')).order_by('-number')


    context= {'profile':profile, 'top_posts':top_posts, 'recent_posts':recent_posts, 'top_authors':top_authors}
    return render(request, 'app/author.html', context)


def search_posts(request):
    search_query= ''
    if request.GET.get('q'):
        search_query= request.GET.get('q')
    posts= Post.objects.filter(title__icontains=search_query)
    print('search:',search_query)
    context= {'posts':posts, 'search_query':search_query}
    return render(request, 'app/search.html', context)


def about(request):
    website_info= None

    if WebsiteMeta.objects.all().exists():
        website_info= WebsiteMeta.objects.all()[0]
    context={'website_info':website_info}
    return render(request, 'app/about.html', context)

def logged_out(request):
    return render(request, 'registration/logged_out.html')

def register_user(request):
    form= NewUserForm()
    if request.POST:
        form= NewUserForm(request.POST)
        if form.is_valid():
            user= form.save()
            login(request, user)
            return redirect('/')
    context={"form": form}
    return render(request, 'registration/registration.html', context)


def bookmark_post(request, slug):
    post= get_object_or_404(Post, slug=slug)
    if post.bookmarks.filter(id=request.user.id).exists():
        post.bookmarks.remove(request.user)
    else:
        post.bookmarks.add(request.user)
    return HttpResponseRedirect(reverse('post_page', args=[str(slug)]))

def like_post(request, slug):
    post= get_object_or_404(Post, slug=slug)
    if post.like.filter(id=request.user.id).exists():
        post.like.remove(request.user)
    else:
        post.like.add(request.user)
    return HttpResponseRedirect(reverse('post_page', args=[str(slug)]))

def all_bookmarked_posts(request):
    all_bookmarked_posts= Post.objects.filter(bookmarks=request.user)
    context={'all_bookmarked_posts':all_bookmarked_posts}
    return render(request, 'app/all_bookmarked_posts.html', context)

def all_posts(request):
    all_posts= Post.objects.all()
    context={'all_posts':all_posts}
    return render(request, 'app/all_posts.html', context)

def all_likes(request):
    all_likes= Post.objects.filter(like= request.user)
    context= {'all_likes':all_likes}
    return render(request, 'app/all_likes.html', context)