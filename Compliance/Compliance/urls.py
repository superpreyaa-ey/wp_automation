"""
URL configuration for Compliance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.usermanagement.urls')),
    path('rag_pipline/', include('apps.rag_model.urls')),
    path('audit/',include('apps.audit_committee.urls')),
    path('qa_audit/', include('apps.qa_audit.urls')),
    path('workpaper/',include('apps.workpaper_automation.urls')),
    path(r'^celery-progress/', include('celery_progress.urls')),
]
