from django.urls import path
from django.views.decorators.cache import cache_page
app_name = "store"

from .views import ProductListView, ProductCreateView, CategoryCreateView, ProductByCategory, product_delete, export_product_xls

urlpatterns = [
    path('product', ProductListView.as_view(), name='product-list'),
    path('product/search/', ProductByCategory.as_view(), name='product-search'),
    path('product/create/', cache_page(60*10)(ProductCreateView.as_view()), name='product-create'),
    path('category/create/', cache_page(60*10)(CategoryCreateView.as_view()), name='category-create'),
    path('delete/product=<int:product_id>', product_delete, name='product-delete'),
    path('product/report=xls', export_product_xls, name='product-xls-report'),
]