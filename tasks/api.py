from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import *
from .serializers import (
    ProjectSerializer, ColumnSerializer, TaskSerializer, 
    CommentSerializer, TimeTrackingSerializer, UserProfileSerializer
)


class ProjectViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, 
                     mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        
        # Если суперюзер - показываем все проекты, можно фильтровать по пользователю
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            if user_id:
                qs = qs.filter(user_id=user_id)
        else:
            # Обычные пользователи видят только свои проекты
            qs = qs.filter(user=self.request.user)
        
        return qs

    def perform_create(self, serializer):
        # Суперюзер может создавать проекты для любого пользователя
        if self.request.user.is_superuser:
            # Проверяем, указан ли пользователь в данных запроса
            user = serializer.validated_data.get('user', self.request.user)
            serializer.save(user=user)
        else:
            # Обычные пользователи создают проекты только для себя
            serializer.save(user=self.request.user)


class ColumnViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                    mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        
        # Если суперюзер - показываем все колонки
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            project_id = self.request.query_params.get('project_id')
            
            if user_id:
                qs = qs.filter(project__user_id=user_id)
            if project_id:
                qs = qs.filter(project_id=project_id)
        else:
            # Обычные пользователи видят только свои колонки
            qs = qs.filter(project__user=self.request.user)
        
        # Сортируем по проекту и порядку
        qs = qs.order_by('project', 'order')
        return qs

    def perform_create(self, serializer):
        project = serializer.validated_data.get('project')
        
        # Проверяем доступ к проекту
        if not self.request.user.is_superuser and project.user != self.request.user:
            raise serializers.ValidationError(
                {"project": "Вы не можете добавлять колонки в чужие проекты"}
            )
        serializer.save()


class TaskViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        
        # Если суперюзер - показываем все задачи
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
            # Обычные пользователи видят только свои задачи
            qs = qs.filter(column__project__user=self.request.user)
        
        # Сортируем по дате создания (новые первыми)
        qs = qs.order_by('-created_at')
        return qs

    def perform_create(self, serializer):
        column = serializer.validated_data.get('column')
        
        # Проверяем доступ к колонке
        if not self.request.user.is_superuser and column.project.user != self.request.user:
            raise serializers.ValidationError(
                {"column": "Вы не можете добавлять задачи в чужие колонки"}
            )
        
        # Если есть assigned_to и это не суперюзер, проверяем, что это допустимый пользователь
        assigned_to = serializer.validated_data.get('assigned_to')
        if assigned_to and not self.request.user.is_superuser:
            # Здесь можно добавить дополнительную логику проверки
            pass
        
        serializer.save()


class CommentViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                     mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        
        # Если суперюзер - показываем все комментарии
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            task_id = self.request.query_params.get('task_id')
            project_id = self.request.query_params.get('project_id')
            
            if user_id:
                # Фильтр по автору комментария
                qs = qs.filter(user_id=user_id)
            if task_id:
                qs = qs.filter(task_id=task_id)
            if project_id:
                qs = qs.filter(task__column__project_id=project_id)
        else:
            # Обычные пользователи видят только свои комментарии
            qs = qs.filter(task__column__project__user=self.request.user)
        
        # Сортируем по дате создания (новые первыми)
        qs = qs.order_by('-created_at')
        return qs

    def perform_create(self, serializer):
        task = serializer.validated_data.get('task')
        
        # Проверяем доступ к задаче
        if not self.request.user.is_superuser and task.column.project.user != self.request.user:
            raise serializers.ValidationError(
                {"task": "Вы не можете добавлять комментарии к чужим задачам"}
            )
        
        # Суперюзер может создавать комментарии от имени других пользователей
        if self.request.user.is_superuser:
            user = serializer.validated_data.get('user', self.request.user)
            serializer.save(user=user)
        else:
            # Обычные пользователи создают комментарии только от своего имени
            serializer.save(user=self.request.user)


class TimeTrackingViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                          mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = TimeTracking.objects.all()
    serializer_class = TimeTrackingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        
        # Если суперюзер - показываем все таймтрекинги
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            task_id = self.request.query_params.get('task_id')
            project_id = self.request.query_params.get('project_id')
            
            if user_id:
                # Фильтр по пользователю, который отслеживал время
                qs = qs.filter(user_id=user_id)
            if task_id:
                qs = qs.filter(task_id=task_id)
            if project_id:
                qs = qs.filter(task__column__project_id=project_id)
        else:
            # Обычные пользователи видят только свои таймтрекинги
            qs = qs.filter(task__column__project__user=self.request.user)
        
        # Сортируем по времени начала (новые первыми)
        qs = qs.order_by('-start_time')
        return qs

    def perform_create(self, serializer):
        task = serializer.validated_data.get('task')
        
        # Проверяем доступ к задаче
        if not self.request.user.is_superuser and task.column.project.user != self.request.user:
            raise serializers.ValidationError(
                {"task": "Вы не можете отслеживать время для чужих задач"}
            )
        
        # Суперюзер может создавать таймтрекинг для других пользователей
        if self.request.user.is_superuser:
            user = serializer.validated_data.get('user', self.request.user)
            serializer.save(user=user)
        else:
            # Обычные пользователи создают таймтрекинг только для себя
            serializer.save(user=self.request.user)


class UserViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    """
    ViewSet для работы с профилем пользователя.
    Суперюзер может видеть и редактировать все профили.
    Обычные пользователи - только свой профиль.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Суперюзер видит все профили, обычные пользователи - только свой
        """
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            # Суперюзер может фильтровать по пользователю
            user_id = self.request.query_params.get('user_id')
            if user_id:
                qs = qs.filter(user_id=user_id)
        else:
            # Обычные пользователи видят только свой профиль
            qs = qs.filter(user=self.request.user)
        
        return qs

    def get_object(self):
        """
        Возвращает профиль в зависимости от прав пользователя
        """
        # Для суперпользователя при запросе конкретного объекта используем стандартный подход
        if self.request.user.is_superuser and 'pk' in self.kwargs:
            return super().get_object()
        
        # Для обычных пользователей - всегда возвращаем их профиль
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    @action(url_path="my", methods=["GET"], detail=False)
    def get_my(self, request, *args, **kwargs):
        """
        Получить свой профиль
        """
        profile = UserProfile.objects.get_or_create(user=self.request.user)[0]
        serializer = self.get_serializer(profile)
        return Response(serializer.data)