from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView,
    DetailView,
    DeleteView,
    ListView,
    View,
    UpdateView
)

from .models import Category, Comment, Post
from .mixins import CommentMixin, PostMixin
from .forms import CommentForm, PostForm

POSTS_PER_PAGE = settings.POSTS_PER_PAGE
SERVICE_EMAIL = settings.SERVICE_EMAIL


def get_posts_queryset(
        manager=Post.objects,
        apply_filters=True,
        apply_annotations=True
):

    queryset = (
        manager.select_related('category', 'author', 'location')
        .prefetch_related('comment_set')
    )

    if apply_filters:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    if apply_annotations:
        queryset = queryset.annotate(comment_count=Count('comment_set'))
    return queryset.order_by('-pub_date')


class IndexView(ListView):
    template_name = 'blog/index.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        return get_posts_queryset()


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = super().get_queryset()

        obj = super().get_object(queryset)

        if ((obj.author != self.request.user)
                and (not obj.is_published
                     or not obj.category.is_published
                     or obj.pub_date > timezone.now())):
            raise Http404

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment_set.all()
        return context


class CategoryPostsView(ListView):
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
        return get_posts_queryset().filter(category=self.get_category())

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


class EditPostView(PostMixin, UpdateView):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class DeletePostView(PostMixin, DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.object}
        return context

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', 'username')
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})

    def get_object(self, queryset=None):
        return self.request.user


class ProfileView(View):

    def get(self, request, username=None):
        profile = get_object_or_404(User, username=username)
        if request.user == profile:
            posts_list = get_posts_queryset(
                manager=profile.posts.all(),
                apply_filters=False
            )
        else:
            posts_list = get_posts_queryset(
                manager=profile.posts.all()
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
    pk_url_kwarg = 'comment_id'

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['comment_id'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['comment_id']}
        )


class DeleteCommentView(CommentMixin, DeleteView):
    pass


class EditCommentView(CommentMixin, UpdateView):
    form_class = CommentForm
