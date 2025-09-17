from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets


from tasks.models import Task
from tasks.serializers import TaskSerializer

class TasksViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer