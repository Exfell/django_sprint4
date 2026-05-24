from django.db import models
from django.contrib.auth import get_user_model


class AbstracModel(models.Model):
    is_published = models.BooleanField(
        blank=False,
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        blank=False,
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Category(AbstracModel):
    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        blank=False,
        verbose_name='Описание'
    )
    slug = models.SlugField(
        blank=False,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.',
        unique=True
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(AbstracModel):
    name = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


User = get_user_model()


class Post(AbstracModel):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=256,
        blank=False,
    )
    text = models.TextField(
        blank=False,
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        blank=False,
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в '
                  'будущем — можно делать отложенные публикации.'
    )
    image = models.ImageField(verbose_name='Изображение', blank=True, null=True,
                              upload_to='post_image/')  # где хранить изображения
    author = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        null=False,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        blank=False,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория'
    )
    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Comment(AbstracModel):
    text = models.TextField(verbose_name='Текст', blank=False)
    author = models.ForeignKey(User, blank=False, on_delete=models.SET_NULL, null=True) # как решить диллему, чтобы при удалении коммент оставался, но автор всегда должен быть при создании - при создании мы не можем его оставить пустым (blank=False), но вообще Null (после удаления SET_NULL) может быть - как "удалённый аккаунт"
    post = models.ForeignKey(Post,blank=False,on_delete=models.CASCADE,null=False, related_name='comments') # к какому посту относятся, при удалении поста удаляем комментарии
    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)
    def __str__(self):
        return f'{self.text[:10]}...'