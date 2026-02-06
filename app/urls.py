from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tasks import views
from django.http import HttpResponse
from django.urls import path
from tasks import views
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

from tasks.api import *

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'columns', ColumnViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'timetracking', TimeTrackingViewSet)
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path("", views.ShowTaskView.as_view(), name="tasks"),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)