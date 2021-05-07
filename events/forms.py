from django import forms

from .models import Event
from django.forms.widgets import Textarea


class EventCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop('request_user', None)
        request_obj = kwargs.pop('request_obj', None)
        self.obj_instance = kwargs.get('instance', None)
        super(EventCreateForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not self.obj_instance:
            if Event.objects.filter(name=name).exclude(id=self.instance.id).exists():
                raise forms.ValidationError("Задача с таким названием уже существует.")

        return name

    def clean_event_type(self):
        event_type = self.cleaned_data.get("event_type")
        if self.obj_instance:
            return self.obj_instance.event_type
        else:
            return event_type

    def clean_start_date(self):
        start_date = self.cleaned_data.get("start_date")
        if start_date:
            return start_date
        else:
            raise forms.ValidationError("Введите корректную дату начала.")

    def clean_end_date(self):
        end_date = self.cleaned_data.get("end_date")
        if self.clean_start_date() > end_date:
            raise forms.ValidationError("Дата окончания не может быть меньше, чем дата начала")
        return end_date


    class Meta:
        model = Event
        fields = (
            'name',
            'event_type',
            'responsible',
            'start_date',
            'end_date',
            'description',
        )

        widgets = {
            "description": Textarea(attrs={"rows": 7})
        }
