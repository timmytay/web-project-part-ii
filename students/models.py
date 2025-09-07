from django.db import models

# Create your models here.
class Student(models.Model):
    name = models.TextField()
    group_name = models.TextField()