from rest_framework import serializers
from .models import Project, Column, Task, Comment, TimeTracking, User, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    # поля из профиля
    profile_name = serializers.CharField(
        source="userprofile.name",
        required=False,
        allow_null=True
    )
    birthday = serializers.DateField(
        source="userprofile.birthday",
        required=False,
        allow_null=True
    )
    profile_type = serializers.CharField(
        source="userprofile.type",
        required=False,
        allow_null=True
    )

    class Meta:
        model = UserProfile
        fields = "__all__"

    def create(self, validated_data):
        profile_data = validated_data.pop("userprofile", {})

        # создаём пользователя правильно
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email", "")
        )

        # профиль уже создан сигналом!
        profile = user.userprofile

        # обновляем поля профиля
        profile.name = profile_data.get("name", profile.name)
        profile.birthday = profile_data.get("birthday", profile.birthday)
        profile.type = profile_data.get("type", profile.type)

        profile.save()

        return user

class ProjectSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        # Автоматически добавляем текущего пользователя при создании проекта
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'user']

class ColumnSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Column
        fields = ['id', 'name', 'project', 'project_name', 'order']

class TaskSerializer(serializers.ModelSerializer):
    column_name = serializers.CharField(source='column.name', read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    assignee_name = serializers.CharField(source='assignee.username', read_only=True, allow_null=True)
    
    def create(self, validated_data):
        # Автоматически добавляем создателя задачи
        if 'request' in self.context:
            validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'column', 'column_name', 
            'priority', 'status', 'due_date', 'created_at', 'updated_at', 
            'picture', 'creator', 'creator_name', 'assignee', 'assignee_name'
        ]
        read_only_fields = ['creator']  # Поле creator нельзя менять через API

class CommentSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    
    def create(self, validated_data):
        # Автоматически добавляем автора комментария
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    class Meta:
        model = Comment
        fields = ['id', 'task', 'task_title', 'text', 'created_at', 'picture', 'user', 'user_name']
        read_only_fields = ['user']

class TimeTrackingSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    
    def create(self, validated_data):
        # Автоматически добавляем пользователя при создании учета времени
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    class Meta:
        model = TimeTracking
        fields = [
            'id', 'task', 'task_title', 'user', 'user_name',
            'start_time', 'end_time', 'description'
        ]
        read_only_fields = ['user']