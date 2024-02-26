from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Comment, Post


class PostMixin(LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'
    login_url = 'login'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Post, pk=kwargs[self.pk_url_kwarg])

        if obj.author != self.request.user and request.user.is_authenticated:
            return redirect(obj.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'
    login_url = 'login'
    pk_url_kwarg = 'comment_id'
    post_pk_url_kwarg = 'post_id'

    def get_success_url(self):
        post_id = self.kwargs[self.post_pk_url_kwarg]
        return reverse_lazy('blog:post_detail', kwargs={'post_id': post_id})

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(
            Comment,
            pk=kwargs[self.pk_url_kwarg],
            post__id=kwargs['post_id']
        )

        if obj.author != self.request.user and request.user.is_authenticated:
            return redirect(obj.post.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)