from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets


from students.models import Student
from students.serializers import StudentSerializer

class StudentsViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer