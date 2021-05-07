from django.db import models
from django.utils.translation import ugettext_lazy as _
from teams.models import Contact, User


class ProductType(models.Model):
    type_name = models.CharField(max_length=50, verbose_name='Название')

    def __str__(self):
        return f'{self.type_name}'
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Product(models.Model):
    type_product = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True, blank=True, related_name='type', verbose_name='Категория')
    manufacture = models.CharField(max_length=45, null=True, blank=True, verbose_name='Производитель')
    model = models.CharField(max_length=30, verbose_name='Модель')
    inventory_number = models.CharField(_('Инвентарный номер'), null=True, blank=True, max_length=10)
    serial_number = models.CharField(max_length=50, null=True, blank=True, verbose_name='S/N')
    created_by = models.ForeignKey(
        User, related_name="product_created_by_user", null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f'{self.manufacture} {self.model}'

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'
        ordering = ['-id']

# DEAL_STATUS = (
#         ("Не указано", "Не указано"),
#         ("В работе", "В работе"),
#         ("Завершено", "Завершено"),
#     )

# class Deal(models.Model):
#     name = models.CharField(_("Сделка"), max_length=64)
#     created_on = models.DateTimeField(_("Дата"), auto_now_add=True)
#     created_by = models.ForeignKey(
#         User, related_name="deal_created_by_user", null=True, on_delete=models.SET_NULL
#     )
#     deal_type = models.CharField(_("Статус"), max_length=50, choices=DEAL_STATUS, default="Не указано")
#     contacts = models.ManyToManyField(Contact, blank=True, verbose_name='Контактное лицо')
#     price = models.CharField(max_length=15, null=True, blank=True, verbose_name='Сумма сделки')
#     note = models.TextField(max_length=1000, blank=True, verbose_name='Примечание')
