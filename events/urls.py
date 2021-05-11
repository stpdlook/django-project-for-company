from django.urls import path
from django.views.decorators.cache import cache_page

from .views import EventListView, EventSearch ,EventCreateView, EventUpdateView, EventDetailView, event_delete

app_name = "events"

urlpatterns = [
    path('', cache_page(5)(EventListView.as_view()), name='event-list'),
    path('create/', cache_page(60*10)(EventCreateView.as_view()), name='event-create'),
    path('search/', EventSearch.as_view(), name='event-search'),
    path('update/<slug:slug>', cache_page(60)(EventUpdateView.as_view()), name='event-update'),
    path('detail/<slug:slug>/', EventDetailView.as_view(), name='event-detail'),
    path('delete/<slug:event_slug>/', event_delete, name='event-delete'),
]