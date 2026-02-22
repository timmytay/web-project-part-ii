from django.db import models
from django.conf import settings 
from django.dispatch import receiver 
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    user = models.ForeignKey("auth.User", verbose_name="Пользователь", on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name

class Column(models.Model):
    name = models.CharField("Название колонки", max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Проект")
    order = models.IntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Колонка"
        verbose_name_plural = "Колонки"
        ordering = ['order']

    def __str__(self):
        return f"{self.project.name} - {self.name}"

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]

    STATUS_CHOICES = [
        ('todo', 'К выполнению'),
        ('in_progress', 'В работе'),
        ('review', 'На проверке'),
        ('done', 'Выполнено'),
    ]

    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    column = models.ForeignKey(Column, on_delete=models.CASCADE, verbose_name="Колонка")
    priority = models.CharField("Приоритет", max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField("Статус", max_length=15, choices=STATUS_CHOICES, default='todo')
    due_date = models.DateField("Срок выполнения", null=True, blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    picture = models.ImageField("Изображение", null=True, upload_to="tasks")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name="Создатель", null=True, blank=True, related_name='created_tasks')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name="Исполнитель", null=True, blank=True, related_name='assigned_tasks')

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name="Задача")
    text = models.TextField("Текст комментария")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    picture = models.ImageField("Изображение", null=True, upload_to="tasks")
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['created_at']

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор", related_name="comments",null=True, blank=True)

    def __str__(self):
        return f"Комментарий к задаче {self.task.title}"

class TimeTracking(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name="Задача")
    start_time = models.DateTimeField("Время начала")
    end_time = models.DateTimeField("Время окончания", null=True, blank=True)
    description = models.TextField("Описание работы", blank=True)

    class Meta:
        verbose_name = "Учет времени"
        verbose_name_plural = "Учет времени"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="time_trackings", null=True, blank=True)

    def __str__(self):
        return f"Время по задаче {self.task.title}"
    
class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now_add=True,null=True)
    
    class Meta:
        abstract = True

class UserProfile(TimestampModel):
    class Type(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        MANAGER = 'manager', 'Менеджер проекта'
        DEVELOPER = 'developer', 'Разработчик'
        VIEWER = 'viewer', 'Наблюдатель'
    
    name = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True)
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    type = models.TextField(choices=Type, null=True)
        
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def str(self) -> str: 
        return f"{self.name} ({self.get_role_display()})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)