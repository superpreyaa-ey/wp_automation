from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Define your app-specific routes here
    path('committee/', views.dashboard_committee, name='committee'),
    path('createaudit/', views.createaudit, name='createaudit'), # abc
    path('approvalcommittee/', views.approval_committee, name='approval_committee'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)