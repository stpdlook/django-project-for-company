from django.urls import path
from .views import (
    CompanyListView,
    CompanyCreateView,
    CompanyDetailView,
    CompanyUpdateView,
    EmployeeEmailCompanyView,
    InventoryCompanyUpdateView,
    InventoryCompanyView,
    InventoryCreate,
    ContactEmailView,
    ContactListView,
    ContactCreateView,
    SendSMSContactView,
    ContactUpdateView,
    SendSMSView,
    SearchContact,
    EmployeeListView,
    EmployeeEmailView,
    EmployeeUpdateView,
    ProfileView,
    ProfileUpdateView,
    company_delete,
    inventory_company_delete,
    contact_delete,
    employee_delete,
    export_product_xls,
    export_employee_xls,
    export_inventory_xls
    )


app_name = "teams"

urlpatterns = [
    ################################
    path('company', CompanyListView.as_view(), name='company-list'),
    path('company/create/', CompanyCreateView.as_view(), name='company-create'),
    path('company/detail/<slug:slug>/', CompanyDetailView.as_view(), name='company-detail'),

    path('company/detail/<slug:slug>/inventory/', InventoryCompanyView.as_view(), name='company-inventory'),
    path('company/detail/<slug:slug>/inventory/report=xls', export_inventory_xls, name='company-inventory-xls'),
    path('company/detail/<slug:slug>/<int:pk>/inventory/create/', InventoryCreate.as_view(), name='company-inventory-create'),
    path('company/detail/<slug:slug>/inventory/detail/<int:pk>', InventoryCompanyUpdateView.as_view(), name='company-inventory-detail'),
    path('company/delete/<slug:company_slug>/<int:pk_id>', inventory_company_delete, name='company-inventory-delete'),
    path('company/sendsms/<slug:slug>', SendSMSView.as_view(), name='contact-sms'),
    path('company/sendemail/<slug:slug>', EmployeeEmailCompanyView.as_view(), name='contact-email-all'),

    path('company/update/<slug:slug>/', CompanyUpdateView.as_view(), name='company-update'),
    path('company/delete/<slug:company_slug>', company_delete, name='company-delete'),
    ################################
    path('contact/', ContactListView.as_view(), name='contact-list'),
    path('contact/search/', SearchContact.as_view(), name='contact-search'),
    path('contact/create/', ContactCreateView.as_view(), name='contact-create'),
    path('contact/sendsms/contact=<int:pk>', SendSMSContactView.as_view(), name='contact-sendsms'),
    path('contact/send/contact=<int:pk>', ContactEmailView.as_view(), name='contact-email'),
    path('contact/update/contact=<int:pk>', ContactUpdateView.as_view(),name='contact-update'),
    path('contact/delete/contact=<int:contact_id>', contact_delete ,name='contact-delete'),
    path('contact/report=xls', export_product_xls ,name='contact-export-xls'),
    ################################
    path('employee/', EmployeeListView.as_view(), name='employee-list'),
    path('employee/send/employee=<int:pk>', EmployeeEmailView.as_view(), name='employee-email'),
    path('employee/update/employee=<int:pk>', EmployeeUpdateView.as_view(), name='employee-update'),
    path('user/delete/employee=<int:user_id>', employee_delete, name='employee-delete'),
    path('user/report=xls', export_employee_xls, name='employee-export-xls'),
    ################################
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update', ProfileUpdateView.as_view(), name='profile-update'),

]