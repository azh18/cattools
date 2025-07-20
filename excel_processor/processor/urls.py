from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('tools/20250720/', views.excel_tool_page, name='excel_tool_page'),
    path('tools/20250720/upload/', views.upload_files, name='upload_files'),
    path('tools/20250720/status/', views.status, name='status'),
    path('tools/20250720/download/', views.download_result, name='download_result'),
]