from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Employee, Company, Contact, InventoryCompany

class CompanyAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('id', 'name', 'address')

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'phone_number', 'is_personal')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'company', 'phone_number', 'email', 'created_by')
    search_fields = ('first_name', 'last_name', 'company__name', 'phone_number', 'email',)
    list_filter = ('company__name',)

class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'employee', 'pc', 'pc_name')
    search_fields = ('company__name', 'employee', 'pc_name')
    list_filter = ('company__name',)


admin.site.register(User, UserAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(InventoryCompany, InventoryAdmin)
admin.site.register(Contact, ContactAdmin)