from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import (
    CharField, CheckConstraint, EmailField, Q, TextField
)
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

from .managers import APIUserManager
from .validators import (custom_year_validator)


only_admin = Q(role='admin') & Q(is_staff=True)
only_not_admin = Q(role__in=('user', 'moderator')) & Q(is_staff=False)


class User(AbstractUser):
    CHOICES = (
        ('user', 'пользователь'),
        ('moderator', 'модератор'),
        ('admin', 'админ')
    )
    username = CharField(
        _('username'),
        max_length=150,
        unique=True,
        null=True,
        help_text=_('Required. 150 characters or fewer. '
                    'Letters, digits and @/./+/-/_ only.'),
        validators=(AbstractUser.username_validator,),
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    email = EmailField('Email', unique=True)
    role = CharField('Роль', default='user', max_length=9, choices=CHOICES)
    bio = TextField('Биография', blank=True)

    objects = APIUserManager()

    class Meta(AbstractUser.Meta):
        ordering = ('id',)
        constraints = (
            CheckConstraint(
                name='only-admin-must-be-staff',
                check=only_admin | only_not_admin
            ),
        )

    def __str__(self):
        return str(self.username) if self.username else '~empty~'


class Reviews(models.Model):
    CHOOSE_RATING = (MinValueValidator(1, 'Меньше 1 поставить нельзя'),
                     MaxValueValidator(10, 'Больше 10 поставить нельзя'))

    author = models.ForeignKey('User', on_delete=models.CASCADE,
                               related_name='reviews',
                               verbose_name='Автор отзыва')
    title = models.ForeignKey('Titles', on_delete=models.CASCADE,
                              related_name='reviews',
                              verbose_name='Произведение')
    text = models.TextField(verbose_name='Отзыв')
    pub_date = models.DateTimeField(verbose_name='Дата публикации отзыва',
                                    auto_now_add=True)
    score = models.PositiveSmallIntegerField(verbose_name='Оценка',
                                             choices=CHOOSE_RATING)


class Comments(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE,
                               verbose_name='Автор комментария')
    review = models.ForeignKey(Reviews, on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Отзыв')
    text = models.TextField(verbose_name='Текст комментария')
    pub_date = models.DateTimeField(verbose_name='Дата добавления комментария',
                                    auto_now_add=True, )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Categories(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200,
                            unique=True)
    slug = models.SlugField(verbose_name='URL', unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.name}'


class Genres(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200,
                            unique=True)
    slug = models.SlugField(verbose_name='URL', unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return f'{self.name}'


class Titles(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200)
    year = models.IntegerField(
        null=True,
        verbose_name='Год',
        validators=[
            custom_year_validator
        ]
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    genre = models.ManyToManyField(
        Genres,
        verbose_name='Жанр',
        blank=True,
        related_name='titles'
    )
    category = models.ForeignKey(
        Categories,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name='Категория',
        related_name='titles'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name
