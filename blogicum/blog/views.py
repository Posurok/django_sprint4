from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import Post, Category

POSTS_PER_PAGE = 5


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
