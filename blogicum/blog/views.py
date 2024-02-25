from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView,
    DetailView,
    DeleteView,
    ListView,
    UpdateView
)

from .models import Category, Comment, Post
from .mixins import CommentMixin, PostMixin
from .forms import CommentForm, PostForm

POSTS_PER_PAGE = settings.POSTS_PER_PAGE
SERVICE_EMAIL = settings.SERVICE_EMAIL


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

    def get_category(self):
        category_slug = self.kwargs.get('category_slug')
        return get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )

    def get_queryset(self):
        return self.base_query().filter(category=self.get_category())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def mail(self):
        send_mail(
            subject=f'New post added - {self.object.title}',
            message=f'{self.object.author.username} add post!',
            from_email=SERVICE_EMAIL,
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


class EditPostView(LoginRequiredMixin, PostMixin, UpdateView):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class DeletePostView(LoginRequiredMixin, PostMixin, DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.object}
        return context

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})

    def get_object(self, queryset=None):
        return self.request.user


class ProfileView(BaseQueryMixin, ListView):

    def get(self, request, username=None):
        profile = get_object_or_404(User, username=username)
        if request.user == profile:
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


class DeleteCommentView(CommentMixin, LoginRequiredMixin, DeleteView):
    pass

class EditCommentView(CommentMixin, LoginRequiredMixin, UpdateView):
    form_class = CommentForm