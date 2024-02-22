from django.views.generic import View, UpdateView, DetailView, ListView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from .forms import PostForm, CommentForm


from .models import Post, Category, Comment

POSTS_PER_PAGE = 10

class BaseQueryMixin:
    def base_query(self):
        return (
            Post.objects.select_related('category', 'author', 'location')
            .prefetch_related('comment_set').annotate(comment_count=Count('comment_set'))
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

    def get(self, request, username=None):
        if username is None:
            if request.user.is_authenticated:
                username = request.user.username
            else:
                return redirect(reverse('login'))

        profile = get_object_or_404(User, username=username)
        posts_list = (
            Post.objects.filter(
            author__username=username,
            is_published=True
        ).prefetch_related('comment_set')
        .annotate(comment_count=Count('comment_set'))
        )
        paginator = Paginator(posts_list, POSTS_PER_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'blog/profile.html',
                      {'profile': profile, 'page_obj': page_obj})

class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class EditPostView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post


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

class EditCommentView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        post_pk = self.kwargs.get('post_pk')
        return reverse_lazy('blog:post_detail', kwargs={'pk': post_pk})
