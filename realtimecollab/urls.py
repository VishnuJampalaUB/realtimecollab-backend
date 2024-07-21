# realtimecollab/urls.py

from django.contrib import admin
from django.urls import path
from collaboration import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/documents/', views.DocumentListView.as_view(), name='document_list'),
    path('api/documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('api/documents/<int:document_id>/share/', views.ShareDocumentView.as_view(), name='share_document'),
    path('', views.home, name='home'),
]
