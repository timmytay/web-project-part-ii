from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
import random
from datetime import timedelta
from tasks.models import Project, Column, Task, Comment, TimeTracking, UserProfile

class Command(BaseCommand):
    help = 'Генерация тестовых данных для приложения задач'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--projects',
            type=int,
            default=50,
            help='Количество проектов для создания (по умолчанию: 50)'
        )
        parser.add_argument(
            '--tasks',
            type=int,
            default=1000,
            help='Минимальное количество задач для создания (по умолчанию: 1000)'
        )

    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])
        
        users = self.create_users(fake)
        self.create_user_profiles(fake, users)
        projects = self.create_projects(fake, users, options['projects'])
        columns = self.create_columns(fake, projects)
        tasks = self.create_tasks(fake, users, columns, options['tasks'])
        self.create_comments(fake, users, tasks)
        self.create_time_trackings(fake, users, tasks)
        self.print_statistics()

    def create_users(self, fake):
        """создание тестовых пользователей"""
        users = list(User.objects.all())
        
        if len(users) < 20:
            for i in range(20 - len(users)):
                username = fake.user_name()
                email = fake.email()
                
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password='testpassword123',
                        first_name=fake.first_name(),
                        last_name=fake.last_name()
                    )
                    users.append(user)
        
        self.stdout.write(f"Создано/получено {len(users)} пользователей")
        return users

    def create_user_profiles(self, fake, users):
        """создание профилей для пользователей"""
        
        profile_types = ['admin', 'manager', 'developer', 'viewer']
        
        for user in users:
            if not hasattr(user, 'userprofile'):
                UserProfile.objects.create(
                    user=user,
                    name=f"{user.first_name} {user.last_name}",
                    birthday=fake.date_of_birth(minimum_age=20, maximum_age=60),
                    type=random.choice(profile_types)
                )
        
        self.stdout.write(f"Создано {UserProfile.objects.count()} профилей")

    def create_projects(self, fake, users, num_projects):
        """создание проектов"""
        
        projects = list(Project.objects.all())
        
        if len(projects) < num_projects:
            for _ in range(num_projects - len(projects)):
                project = Project.objects.create(
                    name=fake.catch_phrase(),
                    description=fake.text(max_nb_chars=500),
                    user=random.choice(users)
                )
                projects.append(project)
        
        self.stdout.write(f"Создано/получено {len(projects)} проектов")
        return projects

    def create_columns(self, projects):
        """создание колонок для проектов"""
        
        columns = list(Column.objects.all())
        column_names = ['Бэклог', 'К выполнению', 'В работе', 'На проверке', 'Выполнено', 'Архив']
        
        for project in projects:
            existing_columns = Column.objects.filter(project=project).count()
            if existing_columns < 4:
                for i, name in enumerate(random.sample(column_names, min(4, len(column_names)))):
                    column = Column.objects.create(
                        name=name,
                        project=project,
                        order=i
                    )
                    columns.append(column)
        
        self.stdout.write(f"  Создано/получено {len(columns)} колонок")
        return columns

    def create_tasks(self, fake, users, columns, min_tasks):
        """создание задач"""
        
        tasks = list(Task.objects.all())

        if len(tasks) < min_tasks:
            for _ in range(min_tasks - len(tasks)):
                created_at = fake.date_time_between(start_date='-1y', end_date='now')
                due_date = created_at + timedelta(days=random.randint(1, 30))
                
                task = Task.objects.create(
                    title=fake.sentence(nb_words=6),
                    description=fake.text(max_nb_chars=random.randint(100, 1000)),
                    column=random.choice(columns),
                    priority=random.choice(['low', 'medium', 'high']),
                    status=random.choice(['todo', 'in_progress', 'review', 'done']),
                    due_date=due_date.date() if random.random() > 0.3 else None,
                    created_at=created_at,
                    updated_at=created_at + timedelta(hours=random.randint(1, 100)),
                    creator=random.choice(users),
                    assignee=random.choice(users) if random.random() > 0.2 else None
                )
                tasks.append(task)
        
        self.stdout.write(f"  Создано/получено {len(tasks)} задач")
        return tasks

    def create_comments(self, fake, users, tasks):
        """создание комментариев к задачам"""
        
        target_comments = 3000
        current_comments = Comment.objects.count()
        
        if current_comments < target_comments:
            comments_to_create = target_comments - current_comments
            new_comments = []
            
            for _ in range(comments_to_create):
                task = random.choice(tasks)
                created_at = fake.date_time_between(
                    start_date=task.created_at, 
                    end_date='now'
                )
                
                comment = Comment(
                    task=task,
                    text=fake.text(max_nb_chars=random.randint(50, 500)),
                    created_at=created_at,
                    user=random.choice(users)
                )
                new_comments.append(comment)
            
            Comment.objects.bulk_create(new_comments, batch_size=1000)
        
        self.stdout.write(f"  Создано {Comment.objects.count()} комментариев")

    def create_time_trackings(self, fake, users, tasks):
        """создание учета времени"""
        
        target_trackings = 2000
        current_trackings = TimeTracking.objects.count()
        
        if current_trackings < target_trackings:
            trackings_to_create = target_trackings - current_trackings
            new_trackings = []
            
            for _ in range(trackings_to_create):
                task = random.choice(tasks)
                user = random.choice(users)
                start_time = fake.date_time_between(
                    start_date=task.created_at, 
                    end_date='now'
                )
                
                if random.random() > 0.2:
                    end_time = start_time + timedelta(hours=random.randint(1, 8))
                else:
                    end_time = None
                
                tracking = TimeTracking(
                    task=task,
                    user=user,
                    start_time=start_time,
                    end_time=end_time,
                    description=fake.text(max_nb_chars=random.randint(50, 200)) if random.random() > 0.3 else ''
                )
                new_trackings.append(tracking)
            
            TimeTracking.objects.bulk_create(new_trackings, batch_size=1000)
        
        self.stdout.write(f"  Создано {TimeTracking.objects.count()} записей учета времени")

    def print_statistics(self):
        """вывод статистики по данным"""
        
        self.stdout.write(f"Пользователи: {User.objects.count()}")
        self.stdout.write(f"Профили пользователей: {UserProfile.objects.count()}")
        self.stdout.write(f"Проекты: {Project.objects.count()}")
        self.stdout.write(f"Колонки: {Column.objects.count()}")
        self.stdout.write(f"Задачи: {Task.objects.count()}")
        self.stdout.write(f"Комментарии: {Comment.objects.count()}")
        self.stdout.write(f"Учет времени: {TimeTracking.objects.count()}")
        
        self.stdout.write("\nСтатистика по задачам:")
        self.stdout.write(f"  Высокий приоритет: {Task.objects.filter(priority='high').count()}")
        self.stdout.write(f"  Средний приоритет: {Task.objects.filter(priority='medium').count()}")
        self.stdout.write(f"  Низкий приоритет: {Task.objects.filter(priority='low').count()}")
        
        self.stdout.write(f"  К выполнению: {Task.objects.filter(status='todo').count()}")
        self.stdout.write(f"  В работе: {Task.objects.filter(status='in_progress').count()}")
        self.stdout.write(f"  На проверке: {Task.objects.filter(status='review').count()}")
        self.stdout.write(f"  Выполнено: {Task.objects.filter(status='done').count()}")
        """6 задание, то есть факер/фейкер"""