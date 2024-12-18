from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Define your app-specific routes here
    path('landing_page/', views.landing_page, name='landing_page'),
    path('create_audit/', views.create_audit, name='create_audit'), # abc
    path('proc/', views.process, name='process'), # 
    path('all_audit/', views.all_audit, name='all_audit'),
    path('approval/', views.approval, name='approval'),
    path('handle_sheet_request/', views.handle_sheet_request, name='handle_sheet_request'),
    # path(r'^ViewReport/<str:pk_test>/', views.ViewReport, name='ViewReport'),
    path(r'^download_excel/<str:pk_test>/', views.download_excel, name='download_excel'),

]




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)