from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(_('email address'))

#Модель сотрудников
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=45, null=True, blank=True, verbose_name='Должность')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    phone_number = models.CharField(max_length=12, null=True, blank=True, verbose_name='Номер телефона')
    profile_image = models.ImageField(default='default-avatar.png', upload_to='users/', null=True, blank=True, verbose_name='Аватар')
    is_personal = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['-id']

#Модель обслуживаемых компаний
class Company(models.Model):
    name = models.CharField(_('Название'),max_length=50)
    address = models.CharField(_('Адрес'), max_length=60)
    description = models.TextField(_('Описание'), max_length=300, blank=True)
    slug = models.SlugField(max_length=70, verbose_name='url', unique=True)
    created_by = models.ForeignKey(
        User, related_name="company_created_by_user", null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Компания(ю)'
        verbose_name_plural = 'Компании'
        ordering = ['-id']


class InventoryCompany(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    employee = models.CharField(_('Имя работника'), max_length=50)
    pc = models.CharField(_('Характеристики ПК'), max_length=350)
    pc_name = models.CharField(_('Имя ПК'), max_length=30, null=True, blank=True)
    comment = models.TextField(_('Комментарий'), max_length=500, blank=True)

    class Meta:
        verbose_name = 'Инвентаризация'
        verbose_name_plural = 'Инвентаризация'


class Contact(models.Model):
    first_name = models.CharField(_('Имя'), max_length=50)
    last_name = models.CharField(_('Фамилия'), max_length=50)
    patronymic = models.CharField(_('Отчество'), max_length=50, null=True, blank=True)
    birth_date = models.DateField(_('Дата рождения'), null=True, blank=True)
    position = models.CharField(_('Должность'), max_length=45, null=True, blank=True)
    phone_number = models.CharField(_('Телефон'), max_length=12, blank=True)
    email = models.EmailField(_('Email'), blank=True)
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL, related_name='employees', verbose_name='Место работы')
    created_by = models.ForeignKey(
        User, related_name="contact_created_by_user", null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
        ordering = ['-id']


#Функция с сигналом для создания профиля сотрудников
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Employee.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)