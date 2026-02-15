from rest_framework import serializers
from .models import Project, Column, Task, Comment, TimeTracking, User, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email', required=False)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'password',
            'name', 'birthday', 'type',
            'created_at', 'updated_at', 'user'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        
        user = User.objects.create_user(
            username=user_data.get('username'),
            password=validated_data.get('password', ''),
            email=user_data.get('email', '')
        )
        
        profile = user.userprofile
        
        profile.name = validated_data.get('name', profile.name)
        profile.birthday = validated_data.get('birthday', profile.birthday)
        profile.type = validated_data.get('type', profile.type)
        profile.save()
        
        return profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        
        if 'username' in user_data:
            instance.user.username = user_data['username']
        if 'email' in user_data:
            instance.user.email = user_data['email']
        
        password = validated_data.pop('password', None)
        if password:
            instance.user.set_password(password)
        
        instance.user.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class ProjectSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
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
        read_only_fields = ['creator']

class CommentSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    
    def create(self, validated_data):
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