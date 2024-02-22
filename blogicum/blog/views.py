from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import View, UpdateView, DetailView, ListView, \
    CreateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse

from .models import Post, Category

POSTS_PER_PAGE = 10


def base_query():
    base_queryset = (
        Post.objects.select_related('category', 'author', 'location')
        .filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    )

    return base_queryset


def index(request):
    post_list = base_query()[:POSTS_PER_PAGE]

    context = {
        'post_list': post_list,
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    post_detail = get_object_or_404(base_query(), pk=post_id)

    context = {'post': post_detail}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = base_query().filter(category__slug=category_slug)
    context = {
        'post_list': post_list,
        'category': category
    }
    return render(request,
                  'blog/category.html',
                  context)

def create_post(request):
    pass

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name']
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})

    def get_object(self, queryset=None):
        return self.request.user



class ProfileView(View):
    model = User
    def get(self, request, username=None):
        if username is None:
            if request.user.is_authenticated:
                username = request.user.username
            else:
                return redirect(reverse('login'))

        profile = get_object_or_404(User, username=username)
        page_obj = Post.objects.filter(
            author__username=username,
            is_published=True
        )[:POSTS_PER_PAGE]
        return render(
            request,
            'blog/profile.html',
            {'profile': profile, 'page_obj': page_obj}
        )

