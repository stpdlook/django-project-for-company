from django.contrib import admin

from .models import ProductType, Product

class ProcuctAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('id', 'type_product', 'manufacture', 'model', 'inventory_number', 'serial_number', 'created_by')
    search_fields = ('type_product__type_name', 'manufacture', 'model', 'inventory_number', 'serial_number')
    list_filter = ('type_product__type_name',)

class ProcuctTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name')
    search_fields = ('type_name',)

admin.site.register(ProductType, ProcuctTypeAdmin)
admin.site.register(Product, ProcuctAdmin)
