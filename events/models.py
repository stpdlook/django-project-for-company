import arrow
from django.db import models
from teams.models import Contact
from django.utils.translation import ugettext_lazy as _

from teams.models import User, Employee, Contact, Company
from django.urls import reverse

class Event(models.Model):

    
    CALL = "Звонок"
    CONFERENCE = "Конференция"
    MEETING = "Встреча"
    EMAIL = "Email"
    VISITCLIENT = "Выезд на заявку"
    OTHER = "Другое"

    PLANNED = "Запланировано"
    TOOKPLACE = "Состоялось"
    NOTTOOKPLACE = "Не состоялось"

    EVENT_TYPE = (
        (OTHER, "Другое"),
        (CALL, "Звонок"),
        (CONFERENCE, "Совещание"),
        (MEETING, "Встреча"),
        (EMAIL, "Email"),
        (VISITCLIENT, "Выезд на заявку"),
    )

    EVENT_STATUS = (
        (PLANNED, "Запланировано"),
        (TOOKPLACE, "Состоялось"),
        (NOTTOOKPLACE, "Не состоялось")
    )

    name = models.CharField(_("Название"), max_length=30)
    event_type = models.CharField(_("Вид задачи"), choices=EVENT_TYPE, max_length=64, default=OTHER)
    status = models.CharField(_("Статус задачи"), choices=EVENT_STATUS, max_length=64, default=PLANNED)
    slug = models.SlugField(max_length=50, verbose_name='url', unique=True)

    start_date = models.DateField(_("Дата начала"), default=None)
    end_date = models.DateField(_("Дата окончания"), default=None)

    created_on = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    created_by = models.ForeignKey(
        User, related_name="event_created_by_user", null=True, on_delete=models.SET_NULL
    )

    description = models.TextField(_('Описание'), max_length=500, blank=True)
    responsible = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="+", verbose_name='Ответственный')
    
    def __str__(self):
        return f'{self.name}'
    
    # def get_absolute_url(self):
    #     return reverse('events:event-detail', kwargs={'event_slug': self.slug})

    @property
    def created_on_arrow(self):
        return arrow.get(self.created_on).humanize()

    class Meta:
        verbose_name = 'Задачи'
        verbose_name_plural = 'Задачи'
        ordering = ["-created_on"]