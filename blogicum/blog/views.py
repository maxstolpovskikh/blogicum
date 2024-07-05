from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, UserProfileForm
from .mixins import CommentMixin, OnlyAuthorMixin, PostListMixin, PostMixin
from .models import Category, Comment, Post, User
from .service import get_posts


class IndexView(PostListMixin, ListView):
    template_name = 'blog/index.html'


class CategoryPostsView(PostListMixin, ListView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True)
        return super().get_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileView(PostListMixin, ListView):
    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.profile = get_object_or_404(
            User, username=self.kwargs['username'])
        return get_posts(self)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.object.username}
        )


class PostCreateView(PostMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(PostMixin, OnlyAuthorMixin, DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class PostUpdateView(PostMixin, OnlyAuthorMixin, UpdateView):
    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.get_object().id)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post_id = self.kwargs.get('post_id')
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=post_id)
        if obj.author != self.request.user:
            obj = get_object_or_404(get_posts(), id=post_id)
        return obj

    def get_queryset(self):
        return super().get_queryset().select_related(
            'author',
            'category',
            'location'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    pass


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    pass
