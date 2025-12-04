from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('projects/new/', views.create_project, name='create_project'),
    path('projects/<int:pk>/edit/', views.edit_project, name='edit_project'),
    path('projects/<int:pk>/delete/', views.delete_project, name='delete_project'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('search/', views.search_projects, name='search_projects'),
    path('folders/new/', views.create_folder, name='create_folder'),
    path('folders/', views.folder_list, name='folder_list'),
    path('folders/<int:pk>/', views.folder_detail, name='folder_detail'),
    path('folders/<int:pk>/edit/', views.edit_folder, name='edit_folder'),
    path('folders/<int:pk>/delete/', views.delete_folder, name='delete_folder'),
    path('projects/<int:project_pk>/bookmark/', views.add_to_folder, name='add_to_folder'),
    path('bookmarks/<int:bookmark_pk>/remove/', views.remove_bookmark, name='remove_bookmark'),
    path('profile/', views.user_profile, name='user_profile'),
] 