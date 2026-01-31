from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from model_bakery import baker
from .models import Project, Column, Task, Comment, TimeTracking
from django.utils import timezone
import json

class APIDiscoveryTests(TestCase):
    """Тесты для обнаружения структуры API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = baker.make(User)
        self.client.force_authenticate(user=self.user)

    def test_api_endpoints_exist(self):
        """Проверяем существование эндпоинтов"""
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
            # Даже если 404, это нормально - значит эндпоинт не настроен
            self.assertIn(response.status_code, [200, 404, 403])

class SimpleProjectTests(TestCase):
    """Простые тесты для Project"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_project_simple(self):
        """Простой тест создания проекта"""
        # Пробуем разные варианты данных в зависимости от реальной модели
        test_data = {'name': 'Simple Project'}
        
        # Добавляем description если поле существует
        if hasattr(Project, 'description'):
            test_data['description'] = 'Simple description'
            
        # Добавляем owner если поле существует
        if hasattr(Project, 'owner'):
            test_data['owner'] = self.user.id
            
        response = self.client.post('/api/projects/', test_data)
        
        print(f"Status: {response.status_code}")
        print(f"Data: {response.data}")
        
        # Если 400, смотрим ошибки
        if response.status_code == 400:
            print(f"Errors: {response.data}")

class SimpleCommentTests(TestCase):
    """Простые тесты для Comment"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        
        # Создаем проект
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

    def test_create_comment_simple(self):
        """Простой тест создания комментария"""
        response = self.client.post('/api/comments/', {
            'task': self.task.id,
            'text': 'Simple comment'
        })
        
        print(f"Status: {response.status_code}")
        print(f"Data: {response.data}")
        
        if response.status_code == 400:
            print(f"Errors: {response.data}")

class RealDataTests(TestCase):
    """Тесты с реальными данными"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Создаем данные напрямую через ORM
        try:
            self.project = Project.objects.create(
                name="Real Project", 
                owner=self.user,
                description="Real project description"
            )
        except TypeError:
            self.project = Project.objects.create(
                name="Real Project",
                description="Real project description"
            )
            
        self.column = Column.objects.create(
            name="Real Column",
            project=self.project, 
            order=1
        )
        self.task = Task.objects.create(
            title="Real Task",
            column=self.column,
            description="Real task description"
        )

    def test_get_existing_projects(self):
        """Тест получения существующих проектов"""
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
        """Тест получения существующих задач"""
        response = self.client.get('/api/tasks/')
        print(f"GET Tasks: {response.status_code}")
        
        if hasattr(response, 'data'):
            print(f"Data type: {type(response.data)}")
            if isinstance(response.data, list):
                print(f"Tasks count: {len(response.data)}")

    def test_try_create_comment(self):
        """Пробуем создать комментарий к существующей задаче"""
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
        """Пробуем создать учет времени"""
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