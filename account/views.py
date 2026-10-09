from django.shortcuts import render
from django.views.generic import View
from django.db.models import Q
from .models import CustomUser, Subscription
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from account.form import UserProfileForm
from django.contrib import messages
from account.form import CustomUserCreationForm

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .serializers import UserSerializer, RegisterSerializer


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'account/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
   
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
       
        user = authenticate(request, email=email, password=password)
       
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'profile')
            messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверный email или пароль')
   
    return render(request, 'account/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы')
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'account/profile.html', {'user': request.user})


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
   
    return render(request, 'account/edit_profile.html', {'form': form})


class AuthorListView(View):
    '''Поиск и просмотр списка пользователей/авторов'''
    def get(self, request):
        users = CustomUser.objects.filter(is_active=True)
        search_query = request.GET.get('user_search', '')
        
        if search_query:
            users = users.filter(
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) | 
                Q(email__icontains=search_query)
            )
        return render(request, 'account/author_list.html', {'authors': users, 'search_query': search_query})

class ToggleSubscribeView(View):
    '''Логика подписки и отписки'''
    def post(self, request, user_id):
        if not request.user.is_authenticated:
            return redirect('login')
            
        author = CustomUser.objects.get(id=user_id)
        if author == request.user:
            return redirect('profile') 
            
        sub, created = Subscription.objects.get_or_create(follower=request.user, author=author)
        if not created:
            sub.delete()
            
        return redirect(request.META.get('HTTP_REFERER', 'profile'))

class UserDetailView(View):
    '''Просмотр публичного профиля любого зарегистрированного автора'''
    def get(self, request, pk):
        author = CustomUser.objects.get(id=pk)
        if request.user.is_authenticated and author == request.user:
            return redirect('profile')
            
        return render(request, 'account/user_detail.html', {'author_user': author})


class RegisterAPIView(APIView):
    '''API для регистрации нового пользователя (Создание аккаунта)'''
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    '''API для получения токена (Авторизация по Email и Паролю)'''
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username=email, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Неверный email или пароль'}, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPIView(APIView):
    '''API для просмотра и редактирования личного профиля текущего пользователя'''
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
