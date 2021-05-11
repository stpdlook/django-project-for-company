from django.shortcuts import redirect, render
from django.views.generic import TemplateView, CreateView, View
from .mixins import EmployeeStaffRequiredMixin, EmployeeRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from .forms import SignUpForm
from django.contrib.auth import views as auth_views
from django.contrib.auth import get_user_model
from django.shortcuts import Http404
from common.models import Thread, Message

from teams.models import Employee, User
from django.db.models import Q

from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.template import loader, RequestContext
from django.dispatch import receiver
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse


# Регистрация
class SignUpView(CreateView):
    template_name = 'registration/register.html'
    form_class = SignUpForm
    success_url = reverse_lazy("login")

# Кастомный вход
class CustomLoginView(auth_views.LoginView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("teams:profile")
        return super(CustomLoginView, self).get(request, *args, **kwargs)


class DialogView(EmployeeStaffRequiredMixin, View):
    template_name = 'common/chat.html'
    
    def get_context_data(self):
        context = {}
        context['persons'] = get_user_model().objects.all().select_related('employee')
        return context

    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context=context)


class ThreadView(EmployeeStaffRequiredMixin, View):
    template_name = 'common/chat_room.html'

    def get_queryset(self):
        return Thread.objects.by_user(self.request.user)

    def get_object(self):
        other_username = self.kwargs.get('username')
        try:
            self.other_user = get_user_model().objects.get(username=other_username)
        except ObjectDoesNotExist:
            raise Http404
        obj = Thread.objects.get_or_create_personal_thread(self.request.user, self.other_user)
        if obj == None:
            raise Http404
        return obj
    
    def get_context_data(self, **kwargs):
        context = {}
        context['thread'] = self.get_object()
        context['recipient'] = self.other_user
        context['persons'] = get_user_model().objects.all().select_related('employee')
        context['message'] = self.get_object().message_set.all().select_related('sender', 'thread')
        return context

    def get(self, request, **kwargs):
        
        try:
            recipient = get_user_model().objects.get(username=kwargs['username'])
            me = get_user_model().objects.get(username=self.request.user)
        except ObjectDoesNotExist:
            raise Http404

        if not recipient == me:
            context = self.get_context_data(**kwargs)
            return render(request, self.template_name, context=context)
        else:
            raise Http404

    def post(self, request, **kwargs):
        self.object = self.get_object()
        thread = self.get_object()
        data = request.POST
        user = request.user
        text = data.get('message')
        Message.objects.create(sender=user, thread=thread, text=text)
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)
