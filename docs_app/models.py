from django.db import models
from django.contrib.auth.models import User


class Docs(models.Model):
    file_path = models.FileField(
        upload_to='documents/',
        verbose_name='Файл'
    )
    size_file = models.FloatField(
        help_text='Размер файла в КБ',
        verbose_name='Размер (КБ)'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )

    def __str__(self):
        return f"{self.id} — {self.file_path.name}"

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['-uploaded_at']


class UserToDocs(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_docs',
        verbose_name='Пользователь'
    )
    doc = models.ForeignKey(
        Docs,
        on_delete=models.CASCADE,
        related_name='doc_users',
        verbose_name='Документ'
    )

    def __str__(self):
        return f"{self.user.username} → Документ {self.doc.id}"

    class Meta:
        verbose_name = 'Пользователь‑Документ'
        verbose_name_plural = 'Пользователи‑Документы'


class Price(models.Model):
    file_type = models.CharField(
        max_length=10,
        help_text='Расширение (jpg, png, pdf...)',
        verbose_name='Тип файла'
    )
    price = models.FloatField(
        help_text='Цена за 1 КБ',
        verbose_name='Цена (руб/КБ)'
    )

    def __str__(self):
        return f"{self.file_type}: {self.price} руб/КБ"

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'
        ordering = ['file_type']


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Пользователь'
    )
    doc = models.ForeignKey(
        Docs,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Документ'
    )
    order_price = models.FloatField(
        verbose_name='Стоимость заказа'
    )
    payment = models.BooleanField(
        default=False,
        verbose_name='Оплачен'
    )

    def __str__(self):
        status = "Оплачен" if self.payment else "Не оплачен"
        return f"Заказ #{self.id} от {self.user.username} ({status})"

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'