from django.contrib import admin
from .models import Blog, Category


class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'published', 'created_at']
    search_fields = ['title', ]


admin.site.register(Blog, BlogAdmin)
admin.site.register(Category)
