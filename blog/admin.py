from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Post

@admin.register(Post)
class PostAdmin(MarkdownxModelAdmin):  # 改這裡
    list_display = ('title', 'published', 'created_at')
    list_filter = ('published', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}