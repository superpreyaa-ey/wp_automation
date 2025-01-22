from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
urlpatterns = [
    # path('', views.loading, name="loading"),
    path('', views.login_view, name="login"),
    path('logout/', views.logoutUser, name='logout'),
    path('index/', views.index, name="index"),
    path('indivdual/<str:pk>/',views.individualReport, name='individualReport'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)