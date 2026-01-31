from rest_framework import serializers
from .models import Project, Column, Task, Comment, TimeTracking

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at']

class ColumnSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Column
        fields = ['id', 'name', 'project', 'project_name', 'order']

class TaskSerializer(serializers.ModelSerializer):
    column_name = serializers.CharField(source='column.name', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'column', 'column_name', 
            'priority', 'status', 'due_date', 'created_at', 'updated_at', 'picture'
        ]

class CommentSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'task', 'task_title', 'text', 'created_at', 'picture']

class TimeTrackingSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = TimeTracking
        fields = [
            'id', 'task', 'task_title', 
            'start_time', 'end_time', 'description'
        ]