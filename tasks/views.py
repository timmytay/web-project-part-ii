from django.views.generic import TemplateView
from typing import Any
from tasks.models import Task, Project

class ShowTaskView(TemplateView):
    template_name = "tasks/show_tasks.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any] :
        context = super().get_context_data(**kwargs)
        context["tasks"] = Task.objects.all()
        context["projects"] = Project.objects.all()
        return context
