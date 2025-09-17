from django.db import models

# Create your models here.
class Project(models.Model):
    name = models.TextField("Название")

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    name = models.TextField("Название")
    project = models.ForeignKey("Project", on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Задание"
        verbose_name_plural = "Задания"