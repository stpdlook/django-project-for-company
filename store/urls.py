from django.urls import path
app_name = "store"

from .views import ProductListView, ProductCreateView, CategoryCreateView, ProductByCategory, product_delete, export_product_xls

urlpatterns = [
    path('product', ProductListView.as_view(), name='product-list'),
    path('product/search/', ProductByCategory.as_view(), name='product-search'),
    path('product/create/', ProductCreateView.as_view(), name='product-create'),
    path('category/create/', CategoryCreateView.as_view(), name='category-create'),
    path('delete/product=<int:product_id>', product_delete, name='product-delete'),
    path('product/report=xls', export_product_xls, name='product-xls-report'),
]