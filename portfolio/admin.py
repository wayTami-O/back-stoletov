from django.contrib import admin
from .models import Project, ContactMessage, SocialLinks
from django.conf import settings
import requests


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'release_date', 'work_start_date', 'work_end_date', 'updated_at'
    )
    list_filter = ('category', 'release_date', 'work_start_date', 'work_end_date', 'created_at')
    search_fields = ('name', 'subtitle', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (
            'Основное',
            {
                'fields': (
                    'name', 'subtitle', 'description', 'category', 'image'
                )
            },
        ),
        (
            'Даты',
            {
                'fields': (
                    'release_date', 'work_start_date', 'work_end_date'
                )
            },
        ),
        (
            'Ссылки',
            {
                'fields': (
                    'link_google_play', 'link_rustore', 'link_appstore', 'link_github', 'extra_social_link'
                )
            },
        ),
        (
            'Служебное',
            {
                'fields': (
                    'created_at', 'updated_at'
                )
            },
        ),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'created_at')
    search_fields = ('full_name', 'email', 'message')
    readonly_fields = ('full_name', 'email', 'message', 'created_at')

    actions = ['resend_to_telegram']

    def resend_to_telegram(self, request, queryset):
        token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID
        sent = 0
        if token and chat_id:
            for contact in queryset:
                text = (
                    f"Повторная отправка сообщения:\n"
                    f"Имя: {contact.full_name}\n"
                    f"Email: {contact.email}\n"
                    f"Сообщение: {contact.message}"
                )
                try:
                    r = requests.post(
                        f"https://api.telegram.org/bot{token}/sendMessage",
                        json={"chat_id": chat_id, "text": text},
                        timeout=10,
                    )
                    if r.status_code == 200:
                        sent += 1
                except Exception:
                    pass
        self.message_user(request, f"Отправлено в Telegram: {sent}")
    resend_to_telegram.short_description = 'Отправить выбранные сообщения в Telegram'


@admin.register(SocialLinks)
class SocialLinksAdmin(admin.ModelAdmin):
    list_display = ('telegram', 'github', 'linkedin')
