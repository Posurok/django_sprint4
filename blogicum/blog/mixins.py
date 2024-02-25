from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Comment, Post


class PostMixin:
    model = Post
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Post, pk=kwargs['pk'])

        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        if obj.author != self.request.user:
            return redirect(obj.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        post_id = self.kwargs['post_pk']
        return reverse_lazy('blog:post_detail', kwargs={'pk': post_id})

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(
            Comment,
            pk=kwargs['pk'],
            post=kwargs['post_pk']
        )

        if obj.author != self.request.user:
            return redirect(obj.post.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)
