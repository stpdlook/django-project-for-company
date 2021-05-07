from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin
from common.mixins import EmployeeStaffRequiredMixin
from django.contrib.auth.decorators import login_required

from django.views import generic
from .forms import EventCreateForm

from django.http import HttpResponse

from django.utils.crypto import get_random_string

from .models import Event
from django.core.exceptions import PermissionDenied
from pytils.translit import slugify
from django.db.models import Q

# Просмотр задач
class EventListView(EmployeeStaffRequiredMixin, generic.ListView):
    template_name = "events/events_list.html"
    context_object_name = "events"
    paginate_by = 4

    def get_queryset(self):
        user = self.request.user
        if user.employee.is_personal:
            queryset = Event.objects.filter(Q(created_by__username=self.request.user) | Q(responsible__user__username=self.request.user))
        return queryset

# Поиск задач
import datetime
class EventSearch(EmployeeStaffRequiredMixin, generic.ListView):
    template_name = "events/events_search.html"
    context_object_name = "events"
    paginate_by = 4


    def get_queryset(self):
        today = datetime.date.today()
        todayfive = today + datetime.timedelta(days=7)
        return Event.objects.filter(start_date__range=(str(today), str(todayfive)))
    

# Создание задач
class EventCreateView(EmployeeStaffRequiredMixin, generic.CreateView):
    template_name = "events/events_create.html"
    form_class = EventCreateForm

    def get_success_url(self):
        return reverse("events:event-list")

    def form_valid(self, form):
        event = form.save(commit=False)
        event.created_by = self.request.user
        tag = slugify(event.name) + slugify(event.created_on)[:15]
        event.slug = tag
        event.save()
        messages.success(self.request, "Задача создана")
        return super(EventCreateView, self).form_valid(form)

# Доп инфа о задаче
class EventDetailView(EmployeeStaffRequiredMixin, generic.DetailView):
    template_name = "events/events_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        user = self.request.user
        if user.employee.is_personal:
            queryset = Event.objects.all()
        return queryset

# Обновление задачи
class EventUpdateView(EmployeeStaffRequiredMixin, generic.UpdateView):
    template_name = "events/events_update.html"
    form_class = EventCreateForm

    def get_queryset(self):
        user = self.request.user
        if user.employee.is_personal:
            queryset = Event.objects.all()
        return queryset

    def get_success_url(self):
        return reverse("events:event-list")

    def form_valid(self, form):
        event = form.save(commit=False)
        tag = slugify(event.name) + slugify(event.created_on)[:15]
        event.slug = tag
        event.save()
        messages.info(self.request, "Обновлено")
        return super(EventUpdateView, self).form_valid(form)

# Удаление задачи
@login_required
def event_delete(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    if not request.user.is_superuser:
        raise PermissionDenied
    elif not (request.user.employee.is_personal and event.created_by == request.user):
        raise PermissionDenied

    event.delete()
    messages.warning(request, "Удалено")
    return redirect("events:event-list")