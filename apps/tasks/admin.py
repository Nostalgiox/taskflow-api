from django.contrib import admin

from .models import Comment, Task


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "priority", "assignee", "due_date")
    list_filter = ("status", "priority")
    search_fields = ("title", "description")
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("task", "author", "created_at")
