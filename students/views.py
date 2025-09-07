from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


from students.models import Student
from django.views.generic import TemplateView



class ShowStudentsView(TemplateView):
    template_name = "students/show_students.html"

    def get_context_data(self, **kwargs: any) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        context['students'] = Student.objects.all()

        return context