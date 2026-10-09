from django.urls import path
from account import views


urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('authors/', views.AuthorListView.as_view(), name='author_list'),
    path('subscribe/<int:user_id>/', views.ToggleSubscribeView.as_view(), name='toggle_subscribe'),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),

    path('api/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/profile/', views.ProfileAPIView.as_view(), name='api_profile'),
]