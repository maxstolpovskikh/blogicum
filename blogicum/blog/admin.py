from django.contrib import admin

from .models import Category, Comment, Location, Post

admin.site.register(Category)

admin.site.register(Location)

admin.site.register(Comment)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'title',
        'author',
        'location',
        'category')
    search_fields = ['text']
    list_filter = ['is_published']
