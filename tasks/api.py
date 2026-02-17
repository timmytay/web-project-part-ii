from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
import openpyxl
from django.db.models import Count

from .models import *
from .serializers import (
    ProjectSerializer, ColumnSerializer, TaskSerializer, 
    CommentSerializer, TimeTrackingSerializer, UserProfileSerializer
)
"""апи проекта"""
class ProjectViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, 
                     mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            if user_id:
                qs = qs.filter(user_id=user_id)
        else:
            qs = qs.filter(user=self.request.user)
        
        return qs

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            user = serializer.validated_data.get('user', self.request.user)
            serializer.save(user=user)
        else:
            serializer.save(user=self.request.user)

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
    """получение статистики. здесь мы будем просто делать обычное ч-ло проектов, тасков, юзеров, врем. меток и т.д."""
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        stats = qs.aggregate(
            count = Count("*"),
        )
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)
    @action(detail=False, methods=["GET"], url_path="export-excel")
    def export_excel(self, request, *args, **kwargs):
        """
        экспорт проектов в файл Excel. для этого нам нужен опенпихл
        """
        projects = self.get_queryset()
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Проекты"
        
        ws.append(["ID", "Название", "Описание", "Дата создания", "Пользователь"])
        
        for project in projects:
            ws.append([
                project.id,
                project.name,
                project.description or "",
                project.created_at.strftime('%d.%m.%Y %H:%M') if project.created_at else "",
                project.user.username if project.user else "",
            ])
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        """загрузка списка проектов"""
        response['Content-Disposition'] = 'attachment; filename="projects.xlsx"'
        
        wb.save(response)
        return response
"""апи колонок"""
class ColumnViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                    mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            project_id = self.request.query_params.get('project_id')
            
            if user_id:
                qs = qs.filter(project__user_id=user_id)
            if project_id:
                qs = qs.filter(project_id=project_id)
        else:
            qs = qs.filter(project__user=self.request.user)
        
        qs = qs.order_by('project', 'order')
        return qs

    def perform_create(self, serializer):
        project = serializer.validated_data.get('project')
        
        if not self.request.user.is_superuser and project.user != self.request.user:
            raise serializers.ValidationError(
                {"project": "Вы не можете добавлять колонки в чужие проекты"}
            )
        serializer.save()

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        stats = qs.aggregate(
            count = Count("*"),
        )
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

"""апи задания"""
class TaskViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            project_id = self.request.query_params.get('project_id')
            column_id = self.request.query_params.get('column_id')
            
            if user_id:
                qs = qs.filter(column__project__user_id=user_id)
            if project_id:
                qs = qs.filter(column__project_id=project_id)
            if column_id:
                qs = qs.filter(column_id=column_id)
        else:
            qs = qs.filter(column__project__user=self.request.user)
        
        qs = qs.order_by('-created_at')
        return qs

    def perform_create(self, serializer):
        column = serializer.validated_data.get('column')
        
        if not self.request.user.is_superuser and column.project.user != self.request.user:
            raise serializers.ValidationError(
                {"column": "Вы не можете добавлять задачи в чужие колонки"}
            )
        
        assigned_to = serializer.validated_data.get('assigned_to')
        if assigned_to and not self.request.user.is_superuser:
            pass
        
        serializer.save()

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        stats = qs.aggregate(
            count = Count("*"),
        )
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

"""апи коммента"""
class CommentViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                     mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            task_id = self.request.query_params.get('task_id')
            project_id = self.request.query_params.get('project_id')
            
            if user_id:
                qs = qs.filter(user_id=user_id)
            if task_id:
                qs = qs.filter(task_id=task_id)
            if project_id:
                qs = qs.filter(task__column__project_id=project_id)
        else:
            qs = qs.filter(task__column__project__user=self.request.user)
        
        qs = qs.order_by('-created_at')
        return qs

    def perform_create(self, serializer):
        task = serializer.validated_data.get('task')
        
        if not self.request.user.is_superuser and task.column.project.user != self.request.user:
            raise serializers.ValidationError(
                {"task": "Вы не можете добавлять комментарии к чужим задачам"}
            )
        
        if self.request.user.is_superuser:
            user = serializer.validated_data.get('user', self.request.user)
            serializer.save(user=user)
        else:
            serializer.save(user=self.request.user)

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        stats = qs.aggregate(
            count = Count("*"),
        )
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

"""апи метки времени"""
class TimeTrackingViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                          mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = TimeTracking.objects.all()
    serializer_class = TimeTrackingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            task_id = self.request.query_params.get('task_id')
            project_id = self.request.query_params.get('project_id')
            
            if user_id:
                qs = qs.filter(user_id=user_id)
            if task_id:
                qs = qs.filter(task_id=task_id)
            if project_id:
                qs = qs.filter(task__column__project_id=project_id)
        else:
            qs = qs.filter(task__column__project__user=self.request.user)
        
        qs = qs.order_by('-start_time')
        return qs

    def perform_create(self, serializer):
        task = serializer.validated_data.get('task')
        
        if not self.request.user.is_superuser and task.column.project.user != self.request.user:
            raise serializers.ValidationError(
                {"task": "Вы не можете отслеживать время для чужих задач"}
            )
        
        if self.request.user.is_superuser:
            user = serializer.validated_data.get('user', self.request.user)
            serializer.save(user=user)
        else:
            serializer.save(user=self.request.user)

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        stats = qs.aggregate(
            count = Count("*"),
        )
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

"""апи юзверя"""
class UserViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    """
    вьюсет для работы с профилем пользователя
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        суперюзер видит все профили, обычные пользователи только свой
        """
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            if user_id:
                qs = qs.filter(user_id=user_id)
        else:
            qs = qs.filter(user=self.request.user)
        
        return qs

    def get_object(self):
        if self.request.user.is_superuser and 'pk' in self.kwargs:
            return super().get_object()
        
        profile= UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    @action(url_path="my", methods=["GET"], detail=False)
    def get_my(self, request, *args, **kwargs):
        """
        Получить свой профиль
        """
        profile = UserProfile.objects.get_or_create(user=self.request.user)[0]
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(url_path="me", methods=["GET"], detail=False, permission_classes=[])
    def get_me(self, request, *args, **kwargs):
        return Response({
            'username': self.request.user.username,
            'is_authenticated': self.request.user.is_authenticated,
            'is_staff': self.request.user.is_staff,
        })

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        stats = qs.aggregate(
            count = Count("*"),
        )

        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)
    
    @action(url_path="login", methods=["POST"], detail=False, permission_classes=[])
    def process_login(self, *args, **kwargs):
        class LoginSerializer(serializers.Serializer):
            username = serializers.CharField()
            password = serializers.CharField()
        
        serializer = LoginSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)

        if user:
            login(self.request, user)
        else:
            return Response({
                "status": "failed"
            }, status=401
            )
        print(self.request.data)
        return Response({
            "status":"success"
        })
    @action(url_path="logout", methods=["POST"], detail=False, permission_classes=[])
    def process_logout(self, *args, **kwargs):
        logout(self.request)

        return Response({
            "status":"success"
        })
