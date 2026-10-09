from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostView.as_view(), name='home'),
    path('create/', views.CreatePostView.as_view(), name='create_post'),
    path('<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
    path('<int:pk>/edit/', views.EditPostView.as_view(), name='edit_post'),            
    path('<int:pk>/toggle-publish/', views.TogglePublishPostView.as_view(), name='toggle_publish'), 
    path('<int:pk>/delete/', views.DeletePostView.as_view(), name='delete_post'),        
    path('review/<int:pk>/', views.AddComments.as_view(), name='add_comments'),
    path('api/posts/', views.PostListAPIView.as_view(), name='api_post_list'),
    path('api/posts/<int:pk>/', views.PostDetailAPIView.as_view(), name='api_post_detail'),
    path('api/tags/', views.TagListAPIView.as_view(), name='api_tag_list'),
    path('<int:pk>/like/', views.ToggleLikeView.as_view(), name='toggle_like'),
    path('liked/', views.LikedPostsView.as_view(), name='liked_posts'),

]

