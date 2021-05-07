from django.contrib import admin

from .models import Event



class EventAdmin(admin.ModelAdmin):
    save_on_top = True
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('id', 'name', 'event_type', 'start_date', 'end_date', 'created_by')

admin.site.register(Event, EventAdmin)