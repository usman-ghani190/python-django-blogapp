
from django.urls import path
from django.contrib.auth import views as auth_views
from app import views


urlpatterns = [
    path('', views.index, name='index'),
    path('post/<slug:slug>', views.post_page, name='post_page'),
    path('tag/<slug:slug>', views.tag_page, name='tag_page'),
    path('author/<slug:slug>', views.author_page, name='author_page'),
    path('search/', views.search_posts, name='search'),
    path('about/', views.about, name='about'),
    path('logout/', auth_views.LogoutView.as_view(next_page='logged_out'), name='logout'),
    path('logged-out/', views.logged_out, name='logged_out'),
]
