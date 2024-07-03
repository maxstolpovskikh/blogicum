from typing import Final
from datetime import datetime

from django.db.models.base import Model as Model
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.views.generic import (
    CreateView, DeleteView, DetailView, UpdateView,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin


from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserProfileForm


POST_LIST_LEN: Final = 10

User = get_user_model()


def get_posts():
    return Post.objects.select_related(
        'category', 'location', 'author').filter(
        is_published=True,
        category__is_published=True,
        pub_date__date__lt=datetime.now())


def paginator(obj_list, request):
    paginator = Paginator(obj_list, POST_LIST_LEN)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    template = 'blog/index.html'
    page_obj = paginator(get_posts(), request)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def category_posts(request, category_slug):
    category = get_object_or_404(Category,
                                 slug=category_slug,
                                 is_published=True)
    post_list = Post.objects.select_related(
        'category',
        'location',
        'author').filter(is_published=True,
                         category__is_published=True,
                         pub_date__date__lt=datetime.now(),
                         category=category)
    page_obj = paginator(post_list, request)
    template = 'blog/category.html'
    context = {'category': category,
               'page_obj': page_obj}
    return render(request, template, context)


def profile(request, username):
    template = 'blog/profile.html'
    profile = get_object_or_404(User, username=username)
    if request.user == profile:
        post_list = Post.objects.filter(author=profile)
    else:
        post_list = get_posts()
    page_obj = paginator(post_list, request)
    context = {'profile': profile,
               'page_obj': page_obj}
    return render(request, template, context)


@login_required
def edit_profile(request):
    if request.method == 'POST' and request.user.is_authenticated:
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            return redirect('blog:profile', username=username)
    else:
        form = UserProfileForm(instance=request.user)
    context = {'form': form}
    return render(request, 'blog/user.html', context)


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostMixin:
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    pass


class PostDeleteView(OnlyAuthorMixin, PostMixin, DeleteView):
    pass


class PostUpdateView(OnlyAuthorMixin, PostMixin, UpdateView):

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])
        if post.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])
        if post.is_published is True or request.user == post.author:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('post')
        )
        return context


class CommentMixin:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if comment.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class CommentCreateView(LoginRequiredMixin, CreateView):
    post_obj = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_obj.pk})


class CommentUpdateView(CommentMixin, UpdateView):
    pass


class CommentDeleteView(CommentMixin, DeleteView):
    pass
