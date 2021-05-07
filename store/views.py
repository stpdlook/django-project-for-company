import xlwt

from django.http import HttpResponse


from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductModelForm, CategoryModelForm
from .models import Product, ProductType


from common.mixins import EmployeeStaffRequiredMixin

from django.contrib.auth.decorators import login_required

from django.views import generic
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.template.loader import get_template

# Просмотр оборудования
class ProductListView(EmployeeStaffRequiredMixin, generic.ListView):
    template_name = "store/product_list.html"
    context_object_name = "products"
    paginate_by = 15

    def get_queryset(self):
        user = self.request.user
        if user.employee.is_personal:
            queryset = Product.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['types'] = ProductType.objects.all()
        return context


# Создание записи с оборудованием
class ProductCreateView(EmployeeStaffRequiredMixin, generic.CreateView):
    template_name = "store/product_create.html"
    form_class = ProductModelForm

    def get_success_url(self):
        return reverse_lazy("store:product-list")

    def form_valid(self, form):
        product = form.save(commit=False)
        form.instance.inventory_number = get_random_string(10).upper()
        product.created_by = self.request.user
        product.save()
        messages.success(self.request, "Добавлено")
        return super(ProductCreateView, self).form_valid(form)

# Поиск по категории
class ProductByCategory(EmployeeStaffRequiredMixin, generic.ListView):
    template_name = 'store/product_search.html'
    context_object_name = 'products'
    paginate_by = 15

    def get_queryset(self):
        return Product.objects.filter(type_product=self.request.GET.get('type_product'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = ProductType.objects.all()
        context['type_product'] = f"type_product={self.request.GET.get('type_product')}&"
        return context



# Создание записи с категорией
class CategoryCreateView(EmployeeStaffRequiredMixin, generic.CreateView):
    template_name = "store/category_create.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse_lazy("store:product-create")

    def form_valid(self, form):
        category = form.save(commit=False)
        category.save()
        return super(CategoryCreateView, self).form_valid(form)

# Удаление записи
@login_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if not (request.user.employee.is_personal or request.user.is_superuser):
        raise PermissionDenied
    
    product.delete()
    messages.warning(request, "Удалено")
    return redirect("store:product-list")

# Экспорт в xls
@login_required
def export_product_xls(request):
    if request.user.is_authenticated and request.user.employee.is_personal or request.user.is_superuser:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment;filename="Equipment.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Оборудование')

        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['Категория', 'Производитель', 'Модель', 'Инвентарный номер', 'Серийный номер']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()

        rows = Product.objects.all().values_list('type_product__type_name', 'manufacture', 'model', 'inventory_number', 'serial_number')
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)
        return response
    else:
        raise PermissionDenied
