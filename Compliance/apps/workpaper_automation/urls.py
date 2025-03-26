from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Define your app-specific routes here
    path('dashboard_workpaper/', views.dashboard_workpaper, name='dashboard_workpaper'),
    path('createauditwp/', views.createauditwp, name='createauditwp'),
    # path('approvalcommittee/', views.approval_committee, name='approval_committee'),

    path('approvalwp/', views.approvalwp, name='approvalwp'),
    path(r'^download_excel_wp/<str:pk_test>/', views.download_excel_wp, name='download_excel_wp'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)