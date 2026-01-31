# api.py
from rest_framework import mixins, viewsets, permissions
from .models import Project, Column, Task, Comment, TimeTracking
from .serializers import (
    ProjectSerializer, ColumnSerializer, TaskSerializer, 
    CommentSerializer, TimeTrackingSerializer
)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Project.objects.all().order_by('-created_at')


class ColumnViewSet(viewsets.ModelViewSet):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Column.objects.all().order_by('project', 'order')


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Task.objects.all().order_by('-created_at')


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Comment.objects.all().order_by('-created_at')


class TimeTrackingViewSet(viewsets.ModelViewSet):
    queryset = TimeTracking.objects.all()
    serializer_class = TimeTrackingSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return TimeTracking.objects.all().order_by('-start_time')
