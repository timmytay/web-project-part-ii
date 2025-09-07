from rest_framework import serializers

from students.models import Group, Student


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'name', 'group']