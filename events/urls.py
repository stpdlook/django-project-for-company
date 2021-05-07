from django.urls import path

from .views import EventListView, EventSearch ,EventCreateView, EventUpdateView, EventDetailView, event_delete

app_name = "events"

urlpatterns = [
    path('', EventListView.as_view(), name='event-list'),
    path('create/', EventCreateView.as_view(), name='event-create'),
    path('search/', EventSearch.as_view(), name='event-search'),
    path('update/<slug:slug>', EventUpdateView.as_view(), name='event-update'),
    path('detail/<slug:slug>/', EventDetailView.as_view(), name='event-detail'),
    path('delete/<slug:event_slug>/', event_delete, name='event-delete'),
]