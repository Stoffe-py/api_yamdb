from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Categories, Comments, Genres, Reviews, Titles, User


@admin.register(User)
class APIUserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'role',
        'first_name',
        'last_name',
        'bio',
        'is_staff',
        'is_superuser'
    )
    list_display_links = (
        'id',
        'username'
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': (
            'email',
            'role',
            'is_staff',
            'is_superuser'
        )}),
    )
    ordering = (
        'id',
    )


@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):

    list_display = ('title', 'score', 'text', 'author', 'pub_date')
    list_display_links = ('text',)
    readonly_fields = ('author', )
    list_filter = ('pub_date',)
    search_fields = ('text',)
    ordering = ('-pub_date',)


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('review', 'text', 'author', 'pub_date')
    list_display_links = ('text',)
    readonly_fields = ('author',)
    list_filter = ('pub_date',)
    search_fields = ('text',)
    ordering = ('-pub_date',)


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_display_links = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Genres)
class GenresAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_display_links = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Titles)
class TitlesAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'description', 'category')
    list_display_links = ('name',)
    list_filter = ('category', 'genre')
    search_fields = ('name',)
    ordering = ('name',)
    empty_value_display = '--нет--'
