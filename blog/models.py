from django.db import models
from django.conf import settings

# Create your models here.

class Tag(models.Model):
    '''Теги для фильтрации статей'''
    name = models.CharField('Название тега', max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

class Post(models.Model):
    '''данные о записи'''
    title = models.CharField('Заголовок записи', max_length=100)
    description = models.TextField('текст записи')
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name='Автор статьи',
        related_name='posts'
    )
    date = models.DateField('Дата публикации')
    image = models.ImageField('Изображения', upload_to='image/%Y', blank=True, null=True)
    is_published = models.BooleanField('Опубликовано', default=True)
    tags = models.ManyToManyField(Tag, verbose_name='Теги', blank=True, related_name='posts')

    def __str__(self):
        return f'{self.title}, {self.author.email}'

    class Meta:
        verbose_name = 'Записи'
        verbose_name_plural = 'Записи'

class Comments(models.Model):
    '''комментарий'''
    email= models.EmailField()
    name = models.CharField('Имя', max_length=50)
    text_comments = models.TextField('Текст комментариев', max_length=200)
    post = models.ForeignKey(Post, verbose_name='Публикация', on_delete=models.CASCADE)


    def __str__(self):
            return f'{self.name}, {self.post}'
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарий'


class Like(models.Model):
    '''Лайки к публикациям'''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name='Кто лайкнул'
    )
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        verbose_name='Публикация', 
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        unique_together = ('user', 'post')

    def __str__(self):
        return f'{self.user.email} -> {self.post.title}'




