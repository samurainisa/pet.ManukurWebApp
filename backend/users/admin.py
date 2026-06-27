from django.contrib import admin

from users.models import MasterProfile, PublicReview, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role', 'client', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'client__full_name', 'client__phone')


@admin.register(MasterProfile)
class MasterProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_name', 'user', 'phone', 'city', 'created_at')
    search_fields = ('display_name', 'phone', 'city', 'address', 'user__username')


@admin.register(PublicReview)
class PublicReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_name', 'rating', 'is_published', 'created_at')
    list_filter = ('rating', 'is_published')
    search_fields = ('client_name', 'text')

