from django.contrib import admin

from .models import Category, Comment, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title', 'description')
    list_filter = ('is_published',)
    list_display_links = ('title',)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'created_at',
        'author',
        'post',
        'is_published',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('text', 'author')
    list_filter = ('author', 'is_published')
    list_display_links = ('text',)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'short_text',
        'author',
        'pub_date',
        'location',
        'category',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title', 'author', 'category')
    list_filter = ('is_published', 'category', 'location', 'pub_date')
    list_display_links = ('title',)

    def short_text(self, obj):
        max_length = 100
        if len(obj.text) > max_length:
            return f'{obj.text[:max_length]}...'
        return obj.text

    short_text.short_description = 'Текст'


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('name',)
    list_filter = ('is_published',)
    list_display_links = ('name',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)