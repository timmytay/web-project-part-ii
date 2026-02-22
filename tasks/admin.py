from django.contrib import admin
from .models import Project, Column, Task, Comment, TimeTracking

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']

@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'project', 'order']
    list_filter = ['project']
    search_fields = ['name']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'column', 'priority', 'status', 'created_at']
    list_filter = ['column', 'priority', 'status', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text']
    date_hierarchy = 'created_at'

@admin.register(TimeTracking)
class TimeTrackingAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'start_time', 'end_time']
    list_filter = ['start_time']
    search_fields = ['description']
    date_hierarchy = 'start_time'