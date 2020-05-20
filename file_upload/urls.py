from django.urls import path

from . import views

urlpatterns = [
    path('', views.opencv, name='opencv'),
    # path('', views.file_upload, name='file_upload'),

]

