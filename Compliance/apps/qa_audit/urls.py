from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # path('landing_page/', views.landing_page, name='landing_page'),
    path('createaudit/', views.create_qa_audit, name='create_qa_audit'), # abc
    # path('proc/', views.process, name='process'), # 
    # path('all_audit/', views.all_audit, name='all_audit'),
    path('approval/', views.qa_approval, name='qa_approval'),
    path('sheet_request/', views.sheet_request, name='sheet_request'),

    path(r'^downloadexcel/<str:pk_test>/', views.downloadexcel, name='downloadexcel'),

]




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)