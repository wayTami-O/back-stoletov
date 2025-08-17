from django.urls import path
from . import views


urlpatterns = [
    path('', views.ProjectListView.as_view(), name='home'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('contact/', views.contact_view, name='contact'),
    # API
    path('api/projects/', views.projects_api, name='projects_api'),
    path('api/projects/<int:pk>/', views.project_detail_api, name='project_detail_api'),
    path('api/contact/', views.contact_api, name='contact_api'),
    path('api/social-links/', views.social_links_api, name='social_links_api'),
    path('api/swagger.json', views.swagger_json, name='swagger_json'),
    path('api/docs/', views.ProjectListView.as_view(template_name='portfolio/swagger.html'), name='swagger_ui'),
]

