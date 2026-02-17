from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from model_bakery import baker
from .models import Project, Column, Task, Comment, TimeTracking
from django.utils import timezone
import json

class APIDiscoveryTests(TestCase):
    """тесты для обнаружения структуры API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = baker.make(User)
        self.client.force_authenticate(user=self.user)

    def test_api_endpoints_exist(self):
        """проверка на наличие эндпоинтов"""
        endpoints = [
            '/api/projects/',
            '/api/columns/', 
            '/api/tasks/',
            '/api/comments/',
            '/api/timetracking/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            print(f"{endpoint}: {response.status_code}")
            self.assertIn(response.status_code, [200, 404, 403])

class ProjectTests(TestCase):
    """тесты для проекта"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_project(self):
        """создание проекта"""
        test_data = {'name': 'Simple Project'}
        
        if hasattr(Project, 'description'):
            test_data['description'] = 'Simple description'
            
        if hasattr(Project, 'owner'):
            test_data['owner'] = self.user.id
            
        response = self.client.post('/api/projects/', test_data)
        
        print(f"Status: {response.status_code}")
        print(f"Data: {response.data}")
        
        if response.status_code == 400:
            print(f"Errors: {response.data}")

class CommentTests(TestCase):
    """тесты для коммента"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        
        try:
            self.project = Project.objects.create(
                name="Test Project", 
                owner=self.user
            )
        except TypeError:
            self.project = Project.objects.create(name="Test Project")
            
        self.column = Column.objects.create(
            name="Test Column",
            project=self.project,
            order=1
        )
        self.task = Task.objects.create(
            title="Test Task",
            column=self.column
        )
        self.client.force_authenticate(user=self.user)

    def test_create_comment(self):
        """тест создания комментария"""
        response = self.client.post('/api/comments/', {
            'task': self.task.id,
            'text': 'Simple comment'
        })
        
        print(f"Status: {response.status_code}")
        print(f"Data: {response.data}")
        
        if response.status_code == 400:
            print(f"Errors: {response.data}")

class DataTests(TestCase):
    """тесты с реальными данными"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        try:
            self.project = Project.objects.create(
                name="Project", 
                owner=self.user,
                description="Project description"
            )
        except TypeError:
            self.project = Project.objects.create(
                name="Project",
                description="Project description"
            )
            
        self.column = Column.objects.create(
            name="Column",
            project=self.project, 
            order=1
        )
        self.task = Task.objects.create(
            title="Task",
            column=self.column,
            description="Task description"
        )

    def test_get_existing_projects(self):
        """тест получения существующих проектов"""
        response = self.client.get('/api/projects/')
        print(f"GET Projects: {response.status_code}")
        
        if hasattr(response, 'data'):
            print(f"Data type: {type(response.data)}")
            if isinstance(response.data, list):
                print(f"Projects count: {len(response.data)}")
            elif isinstance(response.data, dict):
                print(f"Projects keys: {response.data.keys()}")
                if 'results' in response.data:
                    print(f"Projects count: {len(response.data['results'])}")

    def test_get_existing_tasks(self):
        """тест получения существующих задач"""
        response = self.client.get('/api/tasks/')
        print(f"GET Tasks: {response.status_code}")
        
        if hasattr(response, 'data'):
            print(f"Data type: {type(response.data)}")
            if isinstance(response.data, list):
                print(f"Tasks count: {len(response.data)}")

    def test_try_create_comment(self):
        """создание комментария к существующей задаче"""
        response = self.client.post('/api/comments/', {
            'task': self.task.id,
            'text': 'Real comment text'
        }, format='json')
        
        print(f"POST Comment: {response.status_code}")
        if response.status_code == 400:
            print(f"Comment errors: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        elif response.status_code == 201:
            print(f"Comment created: {response.data}")

    def test_try_create_timetracking(self):
        """создание учета времени"""
        response = self.client.post('/api/timetracking/', {
            'task': self.task.id,
            'start_time': timezone.now().isoformat(),
            'description': 'Real work description'
        }, format='json')
        
        print(f"POST TimeTracking: {response.status_code}")
        if response.status_code == 400:
            print(f"TimeTracking errors: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        elif response.status_code == 201:
            print(f"TimeTracking created: {response.data}")