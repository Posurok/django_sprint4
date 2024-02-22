from django.views.generic import View, UpdateView, DetailView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse

from .models import Post, Category

POSTS_PER_PAGE = 10

class BaseQueryMixin:
    def base_query(self):
        return (
            Post.objects.select_related('category', 'author', 'location')
            .filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        )

class IndexView(BaseQueryMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'page_obj'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        return self.base_query()


class PostDetailView(BaseQueryMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return self.base_query()


class CategoryPostsView(BaseQueryMixin, ListView):
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = Category.objects.get(slug=category_slug)
        return self.base_query().filter(category=category)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        category = Category.objects.get(slug=category_slug)
        context['category'] = category
        return context


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
    model = User

    def get(self, request, username=None):
        if username is None:
            if request.user.is_authenticated:
                username = request.user.username
            else:
                return redirect(reverse('login'))

        profile = get_object_or_404(User, username=username)
        page_obj = self.base_query().filter(
            author__username=username
        )[:POSTS_PER_PAGE]
        return render(
            request,
            'blog/profile.html',
            {'profile': profile, 'page_obj': page_obj}
        )

def create_post(request):
    pass
