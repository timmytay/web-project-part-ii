from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


from tasks.models import Task
from django.views.generic import TemplateView



class ShowTasksView(TemplateView):
    template_name = "tasks/show_tasks.html"

    def get_context_data(self, **kwargs: any) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        context['projects'] = Task.objects.all()

        return context