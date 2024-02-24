from django.views.generic import (
    View,
    UpdateView,
    DetailView,
    ListView,
    CreateView,
    DeleteView
)
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.core.mail import send_mail

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm


POSTS_PER_PAGE = 10

class BaseQueryMixin:
    def base_query(self):
        return (
            Post.objects.select_related('category', 'author', 'location')
            .prefetch_related('comment_set')
            .annotate(comment_count=Count('comment_set'))
            .filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            ).order_by('-pub_date')
        )


class IndexView(BaseQueryMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        return self.base_query()


class PostDetailView(BaseQueryMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = self.model.objects.all()
        obj = super().get_object(queryset)
        if obj.author == self.request.user:
            return (
                Post.objects.select_related('category', 'author', 'location')
                .filter(author__username=self.request.user.username)
                .prefetch_related('comment_set')
                .annotate(comment_count=Count('comment_set'))
                .order_by('-pub_date')
            )
        else:
            return self.base_query()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment_set.all()
        return context


class CategoryPostsView(BaseQueryMixin, ListView):
    template_name = 'blog/category.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
        return self.base_query().filter(category=category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
        context['category'] = category
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def mail(self):
        send_mail(
            subject=f'New post added - {self.object.title}',
            message=f'{self.object.author.username} add post!',
            from_email='info@badger.com',
            recipient_list=['badger@badger.com'],
            fail_silently=True,
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        self.mail()
        return response

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class EditPostView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Post, pk=kwargs['pk'])

        if obj.author != self.request.user:
            return redirect(obj.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)


class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.object}
        return context

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Post, pk=kwargs['pk'])

        if obj.author != self.request.user:
            return redirect(obj.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})

    def get_object(self, queryset=None):
        return self.request.user


class ProfileView(BaseQueryMixin, View):

    def get(self, request, username=None):
        if username is None:
            if request.user.is_authenticated:
                username = request.user.username
            else:
                return redirect(reverse('login'))

        profile = get_object_or_404(User, username=username)
        if request.user.username.lower() == username.lower():
            posts_list = (
                Post.objects.select_related('category', 'author', 'location')
                .filter(author__username=username)
                .prefetch_related('comment_set')
                .annotate(comment_count=Count('comment_set'))
                .order_by('-pub_date')
            )
        else:
            posts_list = (
                self.base_query().filter(
                    author__username=username
                )
            )

        paginator = Paginator(posts_list, POSTS_PER_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'blog/profile.html',
                      {'profile': profile, 'page_obj': page_obj})


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'includes/comments.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']}
        )


class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        post = self.get_object().post
        return reverse_lazy('blog:post_detail', kwargs={'pk': post.pk})

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Comment, pk=kwargs['pk'])

        if obj.author != self.request.user:
            return redirect(obj.post.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)


class EditCommentView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        post_pk = self.kwargs.get('post_pk')
        return reverse_lazy('blog:post_detail', kwargs={'pk': post_pk})

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Comment, pk=kwargs['pk'])

        if obj.author != self.request.user:
            return redirect(obj.post.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)
