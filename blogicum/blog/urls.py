from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(pk_url_kwarg='post_id'),
        name='post_detail'
    ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryPostsView.as_view(),
        name='category_posts'
    ),
    path('posts/create/', views.CreatePostView.as_view(), name='create_post'),
    path(
        'posts/<int:post_id>/edit/',
        views.EditPostView.as_view(pk_url_kwarg='post_id'),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.DeletePostView.as_view(pk_url_kwarg='post_id'),
        name='delete_post'
    ),
    path(
        'posts/<int:comment_id>/comment/',
        views.AddCommentView.as_view(pk_url_kwarg='comment_id'),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.DeleteCommentView.as_view(pk_url_kwarg='comment_id', post_pk_url_kwarg='post_id'),
        name='delete_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.EditCommentView.as_view(pk_url_kwarg='comment_id', post_pk_url_kwarg='post_id'),
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
