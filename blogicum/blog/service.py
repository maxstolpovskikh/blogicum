from django.db.models import Count
from django.utils import timezone

from .models import Post


def get_posts(self=None):
    qs = Post.objects.select_related('category', 'location', 'author')
    if not self or self.request.user != self.profile:
        qs = qs.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    else:
        qs = qs.filter(author=self.profile)
    return qs.annotate(comment_count=Count('comments')).order_by('-pub_date')
