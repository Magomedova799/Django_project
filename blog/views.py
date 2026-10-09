from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .models import Post, Tag, Comments
from .models import Like
from .form import CommentsForms, PostForm
from .serializers import PostSerializer, TagSerializer

class PostView(View):
    '''Вывод записей с поиском по заголовкам и тегам на главную страницу'''
    def get(self, request):
        posts = Post.objects.filter(is_published=True)
        
        search_query = request.GET.get('search', '')
        if search_query:
            posts = posts.filter(
                Q(title__icontains=search_query) | 
                Q(tags__name__icontains=search_query)
            ).distinct()
            
        return render(request, 'blog/blog.html', {'post_list': posts})


class PostDetail(View):
    '''Отдельная страница полной записи'''
    def get(self, request, pk):
        post = Post.objects.get(id=pk)
        form = CommentsForms()
        return render(request, 'blog/blog_detail.html', {'post': post, 'form': form})


class CreatePostView(LoginRequiredMixin, View):
    '''Создание новой статьи'''
    login_url = reverse_lazy('register') 
    
    def get(self, request):
        form = PostForm()
        return render(request, 'blog/create_post.html', {'form': form})

    def post(self, request):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user 
            post.date = timezone.now().date()
            post.save()
            return redirect('home')
        return render(request, 'blog/create_post.html', {'form': form})


class EditPostView(LoginRequiredMixin, View):
    '''Редактирование статьи (Доступно только автору или админу)'''
    def get(self, request, pk):
        post = Post.objects.get(id=pk)
        if post.author != request.user and not request.user.is_staff:
            raise PermissionDenied
        
        form = PostForm(instance=post)
        return render(request, 'blog/edit_post.html', {'form': form, 'post': post})

    def post(self, request, pk):
        post = Post.objects.get(id=pk)
        if post.author != request.user and not request.user.is_staff:
            raise PermissionDenied
        
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=pk)
        return render(request, 'blog/edit_post.html', {'form': form, 'post': post})


class TogglePublishPostView(LoginRequiredMixin, View):
    '''Снять статью с публикации или вернуть обратно'''
    def post(self, request, pk):
        post = Post.objects.get(id=pk)
        if post.author != request.user and not request.user.is_staff:
            raise PermissionDenied
        
        post.is_published = not post.is_published
        post.save()
        
        if not post.is_published:
            return redirect('home')
        return redirect('post_detail', pk=pk)


class DeletePostView(LoginRequiredMixin, View):
    '''Полное удаление статьи'''
    def post(self, request, pk):
        post = Post.objects.get(id=pk)
        if post.author != request.user and not request.user.is_staff:
            raise PermissionDenied
        
        post.delete()
        return redirect('home')


class AddComments(LoginRequiredMixin, View):
    '''Добавление комментариев (только для зарегистрированных)'''
    login_url = reverse_lazy('login') 

    def post(self, request, pk):
        form = CommentsForms(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post_id = pk
            comment.save()
        return redirect('post_detail', pk=pk)


class LikedPostsView(View):
    '''Страница со всеми лайкнутыми постами текущего пользователя'''
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        likes = request.user.like_set.all()
        return render(request, 'blog/liked_posts.html', {'likes': likes})


class ToggleLikeView(LoginRequiredMixin, View):
    '''Поставить или убрать лайк к публикации'''
    login_url = reverse_lazy('login')

    def post(self, request, pk):
        post = Post.objects.get(id=pk)
        like_queryset = Like.objects.filter(user=request.user, post=post)
        
        if like_queryset.exists():
            like_queryset.delete()
        else:
            Like.objects.create(user=request.user, post=post)
            
        return redirect(request.META.get('HTTP_REFERER', 'home'))


class PostListAPIView(APIView):
    '''API для работы со статьями (Просмотр списка, Поиск, Создание по токену)'''
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.filter(is_published=True)
        search_query = request.GET.get('search', None)
        if search_query:
            posts = posts.filter(title__icontains=search_query)
        tag_query = request.GET.get('tag', None)
        if tag_query:
            posts = posts.filter(tags__name__iexact=tag_query)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailAPIView(APIView):
    '''API для работы с конкретной статьей по ID (Просмотр, Изменение, Удаление по токену)'''
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': 'Статья не найдена'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        post = Post.objects.get(id=pk)
        if post.author != request.user and not request.user.is_staff:
            return Response({'error': 'Нет прав для редактирования'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = Post.objects.get(id=pk)
        if post.author != request.user and not request.user.is_staff:
            return Response({'error': 'Нет прав для удаления'}, status=status.HTTP_403_FORBIDDEN)
        
        post.delete()
        return Response({'message': 'Статья успешно удалена'}, status=status.HTTP_204_NO_CONTENT)


class TagListAPIView(APIView):
    '''API для работы с тегами (Просмотр и добавление по токену)'''
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
