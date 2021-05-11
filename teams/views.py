from django.shortcuts import get_object_or_404, redirect, render, reverse
from common.mixins import EmployeeStaffRequiredMixin, EmployeeRequiredMixin, AdminRequiredMixin

from django.views import generic

from .models import Company, Contact, Employee, User, InventoryCompany
from .forms import CompanyModelForm, ContactModelForm, EmployeeModelForm, UserForm, ProfileModelForm, InventoryCompanyForm, ContactSMSForm

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from pytils.translit import slugify
import xlwt
from django.utils.crypto import get_random_string
from teams.forms import EmailCompanyForm, EmailForm
from django.core.mail import send_mail
from django.core import serializers
from django.core.paginator import Paginator
import json

# Все компании
class CompanyListView(EmployeeStaffRequiredMixin, generic.ListView):
    template_name = "teams/company_list.html"
    context_object_name = "companies"
    paginate_by = 6

    def get_queryset(self):
        user = self.request.user
        if user.employee.is_personal:
            queryset = Company.objects.all()
        return queryset

# Создание компаний
class CompanyCreateView(EmployeeStaffRequiredMixin, generic.CreateView):
    template_name = "teams/company_create.html"
    form_class = CompanyModelForm

    def get_success_url(self):
        return reverse_lazy("teams:company-list")

    def form_valid(self, form):
        company = form.save(commit=False)
        company.created_by = self.request.user
        tag = slugify(company.name)+slugify(company.address)
        company.slug = tag
        company.save()
        messages.success(self.request, "Запись о компании добавлена")
        return super(CompanyCreateView, self).form_valid(form)


# Обновление данных о компании
class CompanyUpdateView(EmployeeStaffRequiredMixin, generic.UpdateView):
    template_name = "teams/company_update.html"
    form_class = CompanyModelForm

    def get_queryset(self):
        user = self.request.user
        if user.employee.is_personal:
            queryset = Company.objects.all()
        return queryset

    def get_success_url(self):
        return reverse_lazy("teams:company-list")

    def form_valid(self, form):
        company = form.save(commit=False)
        tag = slugify(company.name)+slugify(company.address)
        company.slug = tag
        company.save()
        messages.info(self.request, "Данные о компании обновлены")
        return super(CompanyUpdateView, self).form_valid(form)


# Детали о компании
class CompanyDetailView(EmployeeStaffRequiredMixin, generic.DetailView):
    template_name = "teams/company_detail.html"
    context_object_name = "company"

    def get_queryset(self):
        user = self.request.user
        if user.employee.is_personal:
            queryset = Company.objects.all()
        return queryset

class InventoryCompanyUpdateView(EmployeeStaffRequiredMixin, generic.UpdateView):
    template_name = 'teams/company_inventory_update.html'
    form_class = InventoryCompanyForm


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = Company.objects.get(slug=self.kwargs['slug'])
        return context

    # def get(self, request, *args, **kwargs):
    #     company = Company.objects.get(slug=self.kwargs['slug'])
    #     form = self.form_class()
    #     return render(request, self.template_name, {'form': form, 'company': company})

    def get_queryset(self, **kwargs):
        queryset = InventoryCompany.objects.filter(company__slug=self.kwargs['slug'])
        return queryset

    def get_success_url(self):
        return reverse("teams:company-inventory", kwargs={'slug': self.kwargs['slug']})

    def form_valid(self, form, **kwargs):
        company = Company.objects.get(slug=self.kwargs['slug'])
        item = form.save(commit=False)
        item.company = company
        item.save()

        return super(InventoryCompanyUpdateView, self).form_valid(form)


class InventoryCompanyView(EmployeeStaffRequiredMixin, generic.ListView):
    template_name = 'teams/company_inventory.html'
    context_object_name = "item"
    paginate_by = 5

    def get_queryset(self, **kwargs):

        queryset = InventoryCompany.objects.filter(company__slug=self.kwargs['slug'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = Company.objects.get(slug=self.kwargs['slug'])
        return context

@login_required
def inventory_company_delete(request, company_slug, pk_id):
    company = get_object_or_404(InventoryCompany, company__slug=company_slug, pk=pk_id)
    if not (request.user.is_superuser or (request.user.employee.is_personal and company.created_by == request.user)):
        raise PermissionDenied
    
    company.delete()
    return HttpResponseRedirect(reverse("teams:company-inventory", kwargs={'slug': company_slug}))


# Добавление рабочего места к компании

class InventoryCreate(EmployeeStaffRequiredMixin, generic.CreateView):
    template_name = "teams/company_inventory_create.html"
    form_class = InventoryCompanyForm


    def get(self, request, *args, **kwargs):
        company_pk = Company.objects.get(pk=self.kwargs['pk'])
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'company': company_pk})

    def get_success_url(self):
        return reverse("teams:company-inventory", kwargs={'slug': self.kwargs['slug']})

    def form_valid(self, form, **kwargs):
        company = Company.objects.get(pk=self.kwargs['pk'])
        item = form.save(commit=False)
        item.company = company
        item.save()

        return super(InventoryCreate, self).form_valid(form)




# Отчет рабочих мест по компании

@login_required
def export_inventory_xls(request, slug):
    if request.user.is_authenticated and request.user.employee.is_personal or request.user.is_superuser:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment;filename="InventoryByCompany.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Контакты')

        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['Компания', 'Сотрудник', 'Характеристики ПК', 'Имя ПК', 'Комментарий']
        

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()

        rows = InventoryCompany.objects.filter(company__slug=slug).values_list('company__name', 'employee', 'pc', 'pc_name', 'comment',)
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)
        return response
    else:
        raise PermissionDenied



# Удаление компании
@login_required
def company_delete(request, company_slug):
    company = get_object_or_404(Company, slug=company_slug)
    if not (request.user.is_superuser or (request.user.employee.is_personal and company.created_by == request.user)):
        raise PermissionDenied
    
    company.delete()
    return redirect("teams:company-list")



# Просмотр контактов
class ContactListView(EmployeeStaffRequiredMixin, generic.ListView):
    template_name = "teams/contact_list.html"
    context_object_name = "contacts"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        if user.employee.is_personal:
            queryset = Contact.objects.all().select_related('created_by', 'company')
        return queryset


# Создание контактов
class ContactCreateView(EmployeeStaffRequiredMixin, generic.CreateView):
    template_name = "teams/contact_create.html"
    form_class = ContactModelForm

    def get_success_url(self):
        return reverse_lazy("teams:contact-list")

    def form_valid(self, form):
        contact = form.save(commit=False)
        contact.created_by = self.request.user
        contact.save()
        return super(ContactCreateView, self).form_valid(form)

# Обновление контактов
class ContactUpdateView(EmployeeStaffRequiredMixin, generic.UpdateView):
    template_name = "teams/contact_update.html"
    form_class = ContactModelForm

    def get_queryset(self):
        user = self.request.user
        if user.employee.is_personal:
            queryset = Contact.objects.all().select_related('company')
        return queryset

    def get_success_url(self):
        return reverse_lazy("teams:contact-list")

    def form_valid(self, form):
        form.save()
        return super(ContactUpdateView, self).form_valid(form)


# Отправить email контакту
class ContactEmailView(EmployeeRequiredMixin, generic.View):
    template_name = "email.html"
    form_class = EmailForm

    def get(self, request, *args, **kwargs):
        to_email = Contact.objects.get(pk=self.kwargs['pk']).email
        form = self.form_class(user=self.request.user.email, to_user=to_email)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)

        message = self.request.POST['message']
        from_email = self.request.POST['from_email']
        to_email = self.request.POST['to_email']
        subject = self.request.POST['subject']

        send_mail(
            subject, # Имя источника
            message, # Текст сообщения
            from_email, # Источник
            [to_email,] # Получатель
        )

        messages.success(self.request, "Сообщение отправлено")
        return HttpResponseRedirect(reverse_lazy('teams:contact-list'))





# Поиск контактов
class SearchContact(EmployeeStaffRequiredMixin, generic.ListView):
    template_name = 'teams/contact_search.html'
    context_object_name = 'contacts'
    paginate_by = 10

    def get_queryset(self):
        return Contact.objects.filter(last_name__icontains=self.request.GET.get('last_name'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['last_name'] = f"last_name={self.request.GET.get('last_name')}&"
        return context

# Удаление контактов
@login_required
def contact_delete(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    if not (request.user.is_superuser or (request.user.employee.is_personal and contact.created_by == request.user)):
        raise PermissionDenied
    
    contact.delete()
    return redirect("teams:contact-list")

# Экспорт контактов в xls
@login_required
def export_product_xls(request):
    if request.user.is_authenticated and request.user.employee.is_personal or request.user.is_superuser:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment;filename="Contacts.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Контакты')

        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['Фамилия', 'Имя', 'Отчество', 'Дата рождения', 'Должность', 'Телефон', 'Email', 'Компания']
        

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()
        date_str = xlwt.XFStyle()
        date_str.num_format_str = 'dd/mm/yyyy'

        rows = Contact.objects.all().values_list('first_name', 'last_name', 'patronymic', 'birth_date', 'position', 'phone_number', 'email', 'company__name',)
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                if col_num == 3:
                    ws.write(row_num, col_num, row[col_num], date_str)
                else:
                    ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)
        return response
    else:
        raise PermissionDenied

# Список сотрудников
class EmployeeListView(EmployeeRequiredMixin, generic.ListView):
    template_name = "teams/employee_list.html"
    # context_object_name = "employees"
    paginate_by = 15

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            queryset = Employee.objects.all().select_related('user')
        return queryset


# Экспорт сотрудников в xls
@login_required
def export_employee_xls(request):
    if request.user.is_authenticated and request.user.employee.is_personal or request.user.is_superuser:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment;filename="Employees.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Контакты')

        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['Фамилия', 'Имя', 'Должность', 'Дата рождения', 'Телефон', 'Email']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()
        date_str = xlwt.XFStyle()
        date_str.num_format_str = 'dd/mm/yyyy'

        rows = Employee.objects.all().values_list('user__first_name', 'user__last_name', 'position', 'birth_date', 'phone_number', 'user__email',)
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                if col_num == 3:
                    ws.write(row_num, col_num, row[col_num], date_str)
                else:
                    ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)
        return response
    else:
        raise PermissionDenied


# Обновление данных сотрудника
class EmployeeUpdateView(AdminRequiredMixin, generic.UpdateView):
    template_name = "teams/employee_update.html"
    form_class = EmployeeModelForm

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = Employee.objects.all()
        return queryset

    def get_success_url(self):
        return reverse_lazy("teams:employee-list")

    def form_valid(self, form):
        form.save()
        return super(EmployeeUpdateView, self).form_valid(form)

# Написать email сотруднику
class EmployeeEmailView(EmployeeRequiredMixin, generic.View):
    template_name = "email.html"
    form_class = EmailForm

    def get(self, request, *args, **kwargs):
        to_email = Employee.objects.get(user__id=self.kwargs['pk']).user.email
        form = self.form_class(user=self.request.user.email, to_user=to_email)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)

        message = self.request.POST['message']
        from_email = self.request.POST['from_email']
        to_email = self.request.POST['to_email']
        subject = self.request.POST['subject']

        send_mail(
            subject, # Имя источника
            message, # Текст сообщения
            from_email, # Источник
            [to_email,] # Получатель
        )

        messages.success(self.request, "Сообщение отправлено")
        return HttpResponseRedirect(reverse_lazy('teams:employee-list'))


class EmployeeEmailCompanyView(EmployeeRequiredMixin, generic.View):
    template_name = "send_email_all.html"
    form_class = EmailCompanyForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(user=self.request.user.email)
        return render(request, self.template_name, {
            'companie': Company.objects.get(slug=self.kwargs['slug']),
            'form': form,
        })

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)

        message = self.request.POST['message']
        subject = self.request.POST['subject']

        contacts = Contact.objects.exclude(email__exact='').filter(company__slug=self.kwargs['slug'])

        from_email = self.request.POST['from_email']

        for c in contacts:
            send_mail(
                subject, # Имя источника
                message, # Текст сообщения
                from_email, # Источник
                [c.email,] # Получатель
            )
            print(c.email)

        if contacts:
            messages.success(self.request, "Сообщение отправлено")
        return HttpResponseRedirect(reverse_lazy('teams:company-list'))

# Просмотр профиля
class ProfileView(EmployeeRequiredMixin, generic.TemplateView):
    template_name = 'teams/profile.html'

# Обновление профиля
class ProfileUpdateView(EmployeeRequiredMixin, generic.TemplateView):
    user_form = UserForm
    employee_form = ProfileModelForm
    template_name = 'teams/profile_update.html'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request):

        post_data = request.POST or None
        file_data = request.FILES or None

        user_form = UserForm(post_data, instance=request.user)
        employee_form = ProfileModelForm(post_data, file_data, instance=request.user.employee)

        if user_form.is_valid() and employee_form.is_valid():
            user_form.save()
            employee_form.save()
            messages.success(request, 'Ваш профиль успешно обновлен.')
            return HttpResponseRedirect(reverse_lazy('teams:profile'))

        context = self.get_context_data(
            user_form=user_form,
            employee_form=employee_form,
        )

        return self.render_to_response(context)

# Удаление сотрудника
@login_required
def employee_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if not request.user.is_superuser:
        raise PermissionDenied
    
    user.delete()
    return redirect("teams:employee-list")



# Отправить смс контакту

from smsru.service import SmsRuApi

class SendSMSView(EmployeeStaffRequiredMixin, generic.View):

    sms_api = SmsRuApi()
    balance = sms_api.get_balance()
    limits = sms_api.get_limit()
    template_name = 'teams/sms_send.html'
    form_class = ContactSMSForm


    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {
            'companie': Company.objects.get(slug=self.kwargs['slug']),
            'balance': self.balance,
            'limits': self.limits,
            'form': form,
        })

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)

        message = self.request.POST['message']
        contacts = Contact.objects.exclude(phone_number__exact='').filter(company__slug=self.kwargs['slug'])

        if contacts:

            for contact in contacts:

                recipient = contact.phone_number
                send = self.sms_api.send_multi_sms({
                    recipient: message,
                })

                messages.success(self.request, "SMS-сообщения отправлены")
        else:
            messages.warning(self.request, "Что-то не так")

        return HttpResponseRedirect(reverse("teams:company-list"))

class SendSMSContactView(EmployeeStaffRequiredMixin, generic.View):

    sms_api = SmsRuApi()
    balance = sms_api.get_balance()
    limits = sms_api.get_limit()
    template_name = 'teams/sms_send.html'
    form_class = ContactSMSForm


    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {
            'contact': Contact.objects.get(id=self.kwargs['pk']),
            'balance': self.balance,
            'limits': self.limits,
            'form': form,
        })

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)

        message = self.request.POST['message']
        contact = Contact.objects.get(id=self.kwargs['pk'])
        recipient = contact.phone_number
        send = self.sms_api.send_one_sms(recipient, message)

        messages.success(self.request, "SMS-сообщение отправлено")

        return HttpResponseRedirect(reverse("teams:contact-list"))
