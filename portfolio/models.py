from django.db import models


class ProjectCategory(models.TextChoices):
    EXPERIENCE = 'experience', 'Опыт'
    FREELANCE = 'freelance', 'Фриланс'
    PERSONAL = 'personal', 'Персональный'


class Project(models.Model):
    release_date = models.DateField(blank=True, null=True, help_text='Дата релиза')
    work_start_date = models.DateField(blank=True, null=True, help_text='Начало работ')
    work_end_date = models.DateField(blank=True, null=True, help_text='Окончание работ')
    name = models.CharField(max_length=255, verbose_name='Название проекта')
    subtitle = models.CharField(max_length=255, verbose_name='Заголовок', help_text='Краткое описание')
    description = models.TextField(verbose_name='Полное описание')
    description_en = models.TextField(blank=True, null=True, verbose_name='Описание (EN)')

    link_google_play = models.URLField(blank=True, null=True, verbose_name='Google Play')
    link_rustore = models.URLField(blank=True, null=True, verbose_name='RuStore')
    link_appstore = models.URLField(blank=True, null=True, verbose_name='App Store')
    link_github = models.URLField(blank=True, null=True, verbose_name='GitHub')

    image = models.ImageField(upload_to='projects/', blank=True, null=True, verbose_name='Картинка')
    category = models.CharField(
        max_length=20,
        choices=ProjectCategory.choices,
        default=ProjectCategory.PERSONAL,
        verbose_name='Категория',
    )

    extra_social_link = models.URLField(blank=True, null=True, verbose_name='Доп. ссылка (соцсеть)')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self) -> str:
        return self.name


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=255, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    message = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Сообщение с формы'
        verbose_name_plural = 'Сообщения с формы'

    def __str__(self) -> str:
        return f"{self.full_name} <{self.email}>"


class SocialLinks(models.Model):
    telegram = models.URLField(blank=True, null=True, verbose_name='Telegram')
    github = models.URLField(blank=True, null=True, verbose_name='GitHub')
    linkedin = models.URLField(blank=True, null=True, verbose_name='LinkedIn')

    class Meta:
        verbose_name = 'Соц. ссылки'
        verbose_name_plural = 'Соц. ссылки'

    def __str__(self) -> str:
        return 'Соц. ссылки'
