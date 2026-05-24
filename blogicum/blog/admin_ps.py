from django.contrib import admin
from .models import Category, Location, Post


# ==================== НАСТРОЙКИ ДЛЯ КАТЕГОРИЙ ====================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_published', 'created_at')
    readonly_fields = ('created_at',)


# ==================== НАСТРОЙКИ ДЛЯ ЛОКАЦИЙ ====================
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = ('is_published', 'created_at')
    readonly_fields = ('created_at',)


# ==================== НАСТРОЙКИ ДЛЯ ПОСТОВ ====================
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'location', 'pub_date', 'is_published', 'created_at')
    list_editable = ('is_published', 'category', 'location')
    search_fields = ('title', 'text', 'author__username')
    list_filter = ('is_published', 'category', 'location', 'pub_date', 'created_at')
    list_display_links = ('title',)
    date_hierarchy = 'pub_date'
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'text', 'author')
        }),
        ('Публикация', {
            'fields': ('category', 'location', 'pub_date', 'is_published')
        }),
        ('Служебная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)  # сворачиваемый блок
        }),
    )