from django.contrib import admin
from django.utils.html import format_html
from .models import Topic, Article

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'article_count')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'created_at', 'image_preview')
    list_filter = ('topic', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'slug', 'topic')
        }),
        ('Content', {
            'fields': ('content', 'image')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="30" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'
