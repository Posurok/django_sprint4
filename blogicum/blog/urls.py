from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('category/<slug:category_slug>/',
         views.CategoryPostsView.as_view(),
         name='category_posts'),
    path('create_post/', views.create_post, name='create_post'),
    path('edit_profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
