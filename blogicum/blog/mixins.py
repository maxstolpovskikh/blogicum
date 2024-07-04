from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse

from .constants import POST_LIST_LEN
from .forms import CommentForm, PostForm
from .models import Comment, Post
from .service import get_posts


class PostQuerySetMixin:
    def get_queryset(self):
        return get_posts()


class PostListMixin(PostQuerySetMixin):
    context_object_name = 'page_obj'
    paginate_by = POST_LIST_LEN


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostMixin(LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentMixin(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        self.comment = self.get_object()
        if self.comment.author != request.user:
            return redirect('blog:post_detail', post_id=self.comment.post.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})