from django.forms import ValidationError
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, serializers
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from tasks.permissions import SecondFactorPermission
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
import openpyxl
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import *
from .serializers import (
    ProjectSerializer, ColumnSerializer, TaskSerializer, 
    CommentSerializer, TimeTrackingSerializer, UserProfileSerializer
)

"""вопрос: почему нет декоратора?
ответ: потому что у нас уже есть CRUD. без С. следовательно мы назначаем пермишены, если юзер хочет сделать другие операции со страницей"""

class ProjectViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'create', 'destroy']:
            permission_classes = [IsAuthenticated, SecondFactorPermission]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        
        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)
        
        return qs


    def perform_create(self, serializer):
        project = serializer.validated_data.get('project')
    
        if project and not self.request.user.is_superuser and project.user != self.request.user:
            raise serializers.ValidationError(
                {"project": "Вы не можете создавать задачи в чужих проектах"}
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
        stats = Project.objects.aggregate(count = Count("*"))
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=["GET"], url_path="export-excel")
    def export_excel(self, request, *args, **kwargs):
        """экспорт проектов в файл Excel. для этого нам нужен опенпихл"""
        projects = self.get_queryset()
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Проекты"
        
        ws.append(["ID", "Название", "Описание", "Дата создания", "Пользователь"])
        
        for p in projects:
            ws.append([
                p.id,
                p.name,
                p.description or "",
                p.created_at.strftime('%d.%m.%Y %H:%M') if p.created_at else "",
                p.user.username if p.user else "",
            ])
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        response['Content-Disposition'] = 'attachment; filename="projects.xlsx"'
        
        wb.save(response)
        return response
    
class ColumnViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'create', 'destroy']:
            permission_classes = [IsAuthenticated, SecondFactorPermission]
        else:
            permission_classes = []
        
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        
        user_id = self.request.query_params.get('user_id')
        project_id = self.request.query_params.get('project_id')
            
        if user_id:
            qs = qs.filter(project__user_id=user_id)
        if project_id:
            qs = qs.filter(project_id=project_id)
        qs = qs.order_by('project', 'order')
        return qs

    def perform_create(self, serializer):
        project = serializer.validated_data.get('project')
        
        if not self.request.user.is_superuser and project.user != self.request.user:
            raise serializers.ValidationError(
                {"project": "вы не можете добавлять колонки в чужие проекты"}
            )
        serializer.save()

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = Column.objects.aggregate(count = Count("*"))
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

class TaskViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'create', 'destroy']:
            permission_classes = [IsAuthenticated, SecondFactorPermission]
        else:
            permission_classes = []
        
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
    
        user_id = self.request.query_params.get('user_id')
        project_id = self.request.query_params.get('project_id')
        column_id = self.request.query_params.get('column_id')
            
        if user_id:
            qs = qs.filter(column__project__user_id=user_id)
        if project_id:
            qs = qs.filter(column__project_id=project_id)
        if column_id:
            qs = qs.filter(column_id=column_id)
        
        qs = qs.order_by('-created_at')
        return qs

    def perform_create(self, serializer):
        column = serializer.validated_data.get('column')
        
        if not self.request.user.is_superuser and column.project.user != self.request.user:
            raise serializers.ValidationError(
                {"column": "вы не можете добавлять задачи в чужие колонки"}
            )
        
        assigned_to = serializer.validated_data.get('assigned_to')
        if assigned_to and not self.request.user.is_superuser:
            pass
        
        serializer.save()

    class StatsSerializer(serializers.Serializer):
        total = serializers.IntegerField()
        by_status = serializers.DictField(child=serializers.IntegerField())
        by_priority = serializers.DictField(child=serializers.IntegerField())
        overdue = serializers.IntegerField()
        created_week = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):
        qs = Task.objects.all()
        now = timezone.now()
        week_ago = now - timedelta(days=7)

        stats = {
            "total": qs.count(),
            "by_status": dict(
                qs.values("status").annotate(c=Count("id")).values_list("status", "c")
            ),
            "by_priority": dict(
                qs.values("priority").annotate(c=Count("id")).values_list("priority", "c")
            ),
            "overdue": qs.filter(
                due_date__lt=now,
                status__in=["todo", "in_progress", "review"]
            ).count(),
            "created_week": qs.filter(
                created_at__gte=week_ago
            ).count(),
        }

        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

class TimeTrackingViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = TimeTracking.objects.all()
    serializer_class = TimeTrackingSerializer
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'create', 'destroy']:
            permission_classes = [IsAuthenticated, SecondFactorPermission]
        else:
            permission_classes = []
        
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        
        user_id = self.request.query_params.get('user_id')
        task_id = self.request.query_params.get('task_id')
        project_id = self.request.query_params.get('project_id')
            
        if user_id:
            qs = qs.filter(user_id=user_id)
        if task_id:
            qs = qs.filter(task_id=task_id)
        if project_id:
            qs = qs.filter(task__column__project_id=project_id)

        qs = qs.order_by('-start_time')
        return qs

    def perform_create(self, serializer):
        task = serializer.validated_data.get('task')
        
        if not self.request.user.is_superuser and task.column.project.user != self.request.user:
            raise serializers.ValidationError(
                {"task": "вы не можете отслеживать время для чужих задач"}
            )
        
        if self.request.user.is_superuser:
            user = serializer.validated_data.get('user', self.request.user)
            serializer.save(user=user)

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = TimeTracking.objects.aggregate(
            count = Count("*"),
        )
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)
    
class CommentViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                     mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'create', 'destroy']:
            permission_classes = [IsAuthenticated, SecondFactorPermission]
        else:
            permission_classes = []
        
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        task_id = self.request.query_params.get('task_id')
        project_id = self.request.query_params.get('project_id')
            
        if user_id:
            qs = qs.filter(user_id=user_id)
        if task_id:
            qs = qs.filter(task_id=task_id)
        if project_id:
            qs = qs.filter(task__column__project_id=project_id)

        qs = qs.order_by('-created_at')
        return qs

    def perform_create(self, serializer):
        task = serializer.validated_data.get('task')
        
        if not self.request.user.is_superuser and task.column.project.user != self.request.user:
            raise serializers.ValidationError(
                {"task": "вы не можете добавлять комментарии к чужим задачам"}
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
        stats = Comment.objects.aggregate(
            count = Count("*"),
        )
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

class TimeTrackingViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    queryset = TimeTracking.objects.all()
    serializer_class = TimeTrackingSerializer
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'create', 'destroy']:
            permission_classes = [IsAuthenticated, SecondFactorPermission]
        else:
            permission_classes = []
        
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        
        user_id = self.request.query_params.get('user_id')
        task_id = self.request.query_params.get('task_id')
        project_id = self.request.query_params.get('project_id')
            
        if user_id:
            qs = qs.filter(user_id=user_id)
        if task_id:
            qs = qs.filter(task_id=task_id)
        if project_id:
            qs = qs.filter(task__column__project_id=project_id)

        qs = qs.order_by('-start_time')
        return qs

    def perform_create(self, serializer):
        task = serializer.validated_data.get('task')
        
        if not self.request.user.is_superuser and task.column.project.user != self.request.user:
            raise serializers.ValidationError(
                {"task": "вы не можете отслеживать время для чужих задач"}
            )
        
        if self.request.user.is_superuser:
            user = serializer.validated_data.get('user', self.request.user)
            serializer.save(user=user)

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = TimeTracking.objects.aggregate(
            count = Count("*"),
        )
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

class UserViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'create', 'destroy']:
            permission_classes = [IsAuthenticated, SecondFactorPermission]
        else:
            permission_classes = []
        
        return [permission() for permission in permission_classes]

    def get_queryset(self):
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
        
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    """пояснение: у нас есть second (есть ли у юзверя двухфакторка? и expire (когда истечет время?))"""
    @action(url_path="me", methods=["GET"], detail=False, permission_classes=[])
    def get_me(self, request, *args, **kwargs):
        data = {
            'username': self.request.user.username,
            'is_authenticated': self.request.user.is_authenticated,
            'is_staff': self.request.user.is_staff,
        }
        """вся эта конструкция нужна для корректного отображения плашки: по истечении времени экспайр идет на 0, как и секонд"""
        if self.request.user.is_authenticated:
            second = self.request.session.get('second')
            expire = self.request.session.get('second_expire')

            if second and expire:
                if timezone.now().timestamp() > expire:
                    self.request.session.pop('second', None)
                    self.request.session.pop('second_expire', None)
                    second = False
                    expire = None
            else:
                second = False
                expire = None

            data.update({
                'second': second,
                'second_expire': expire,
            })

        return Response(data)

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
            return Response({"status": "failed"}, status=401)
        """нет времени объяснять. он регается"""
        return Response({"status":"success"})
    
    @action(url_path="logout", methods=["POST"], detail=False, permission_classes=[])
    def process_logout(self, *args, **kwargs):
        logout(self.request)
        
        return Response({"status":"success"})
    
    @action(url_path="second-login", methods=["POST"], detail=False, permission_classes=[])
    def second_login(self, *args, **kwargs):
        key = self.request.user.userprofile.totp_key
        t = pyotp.totp.TOTP(key)
        """позже о коде, сейчас мы приводим к инту время, к которому сессия истечёт. у нас это 10 мин"""
        code = self.request.data.get('key')

        if code == t.now():
            self.request.session['second'] = True;
            self.request.session['second_expire'] = int(
            (timezone.now() + timedelta(minutes=10)).timestamp()
        )
            return Response({"status":"success"})
        
    @action(url_path="show-totp", methods=["POST"], detail=False, permission_classes=[])
    def show_totp(self, *args, **kwargs):
        """random_base32 для генерации каждый раз, когда юзер обновляет страницу и у него нет двушки"""

        self.request.user.userprofile.totp_key = pyotp.random_base32()
        self.request.user.userprofile.save()

        """and he shall be named timmie!!!"""
        
        url = pyotp.totp.TOTP(self.request.user.userprofile.totp_key).provisioning_uri(
            name=self.request.user.username, 
            issuer_name="TaskManager",
            )
        
        return Response({
            "url": url
        })