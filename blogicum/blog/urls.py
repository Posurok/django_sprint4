from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path(
        'posts/<int:pk>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryPostsView.as_view(),
        name='category_posts'
    ),
    path('create_post/', views.CreatePostView.as_view(), name='create_post'),
    path(
        'edit_post/<int:pk>/',
        views.EditPostView.as_view(),
        name='edit_post'
    ),
    path(
        'delete_post/<int:pk>/delete/',
        views.DeletePostView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:pk>/comment/',
        views.AddCommentView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_pk>/delete_comment/<int:pk>/',
        views.DeleteCommentView.as_view(),
        name='delete_comment'
    ),
    path(
        'posts/<int:post_pk>/edit_comment/<int:pk>/',
        views.EditCommentView.as_view(),
        name='edit_comment'
    ),
    path(
        'edit_profile/',
        views.EditProfileView.as_view(),
        name='edit_profile'
    ),
    path(
        'profile/<str:username>/',
        views.ProfileView.as_view(),
        name='profile'
    ),
    path(
        'profile/',
        views.ProfileView.as_view(),
        name='profile'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
