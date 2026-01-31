from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tasks import views
from django.http import HttpResponse
from django.urls import path
from tasks import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from tasks.api import (
    ProjectViewSet, 
    ColumnViewSet, 
    TaskViewSet, 
    CommentViewSet, 
    TimeTrackingViewSet)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'columns', ColumnViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'timetracking', TimeTrackingViewSet)

urlpatterns = [
    path("", views.ShowTaskView.as_view(), name="tasks"),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)