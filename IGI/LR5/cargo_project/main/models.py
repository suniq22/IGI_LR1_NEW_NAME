"""Generic informational pages: News, FAQ, Contacts, Vacancies, Reviews, Promo."""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class CompanyInfo(models.Model):
    """О компании — singleton-style table."""
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Описание')
    history = models.TextField(blank=True, verbose_name='История по годам')
    requisites = models.TextField(blank=True, verbose_name='Реквизиты')
    video_url = models.URLField(blank=True, verbose_name='Видео URL')
    logo = models.ImageField(
        upload_to='company/', blank=True, null=True, verbose_name='Логотип'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'О компании'
        verbose_name_plural = 'О компании'

    def __str__(self):
        return self.title


class News(models.Model):
    """News articles for the site."""
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    summary = models.CharField(
        max_length=300, verbose_name='Краткое содержание'
    )
    content = models.TextField(verbose_name='Полный текст')
    image = models.ImageField(
        upload_to='news/', blank=True, null=True, verbose_name='Картинка'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news',
        verbose_name='Автор',
    )
    published_at = models.DateTimeField(default=timezone.now, verbose_name='Опубликовано')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title


class FAQ(models.Model):
    """Словарь терминов и понятий / FAQ."""
    question = models.CharField(max_length=300, verbose_name='Вопрос')
    answer = models.TextField(verbose_name='Ответ')
    added_at = models.DateField(default=timezone.now, verbose_name='Дата добавления')

    class Meta:
        ordering = ['-added_at']
        verbose_name = 'Термин / FAQ'
        verbose_name_plural = 'Словарь терминов и FAQ'

    def __str__(self):
        return self.question


class Contact(models.Model):
    """Сотрудник с фото, описанием, телефоном, почтой."""
    full_name = models.CharField(max_length=120, verbose_name='ФИО')
    position = models.CharField(max_length=120, verbose_name='Должность')
    description = models.TextField(verbose_name='Описание работ')
    phone = models.CharField(max_length=32, verbose_name='Телефон')
    email = models.EmailField(verbose_name='Email')
    photo = models.ImageField(
        upload_to='contacts/', blank=True, null=True, verbose_name='Фото'
    )

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f'{self.full_name} — {self.position}'


class Vacancy(models.Model):
    """Open vacancies."""
    title = models.CharField(max_length=200, verbose_name='Название вакансии')
    description = models.TextField(verbose_name='Описание')
    salary = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Зарплата, BYN'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    posted_at = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-posted_at']
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'

    def __str__(self):
        return self.title


class Review(models.Model):
    """User reviews."""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка',
    )
    text = models.TextField(verbose_name='Текст отзыва')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.author} — {self.rating}/5'


class PromoCode(models.Model):
    """Promo codes / coupons."""
    code = models.CharField(max_length=32, unique=True, verbose_name='Код')
    discount_percent = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(90)],
        verbose_name='Скидка, %',
    )
    description = models.CharField(max_length=200, verbose_name='Описание')
    valid_from = models.DateField(verbose_name='Действует с')
    valid_to = models.DateField(verbose_name='Действует до')
    is_archived = models.BooleanField(default=False, verbose_name='В архиве')

    class Meta:
        ordering = ['-valid_to']
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды и купоны'

    def __str__(self):
        return f'{self.code} (-{self.discount_percent}%)'

    @property
    def is_active(self):
        today = timezone.now().date()
        return (
            not self.is_archived
            and self.valid_from <= today <= self.valid_to
        )
