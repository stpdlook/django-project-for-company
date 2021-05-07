from django import forms
from .models import Product, ProductType

class ProductModelForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = (
            'type_product',
            'manufacture',
            'model',
            'serial_number',
        )
        # widgets = {'inventory_number': forms.HiddenInput()}

class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = (
            'type_name',
        )