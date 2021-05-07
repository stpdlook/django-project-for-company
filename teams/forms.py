from django import forms

from .models import User, Company, Contact, Employee, InventoryCompany

from CRMPlus import settings


class CompanyModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        request_obj = kwargs.pop('request_obj', None)
        self.obj_instance = kwargs.get('instance', None)
        super(CompanyModelForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not self.obj_instance:
            if Company.objects.filter(name=name).exclude(id=self.instance.id).exists():
                raise forms.ValidationError("Компания с таким именем уже существует")
        
        return name


    class Meta:
        model = Company
        fields = (
            'name',
            'address',
            'description',
        )


class ContactModelForm(forms.ModelForm):
    
    class Meta:
        model = Contact
        fields = (
            'first_name',
            'last_name',
            'patronymic',
            'birth_date',
            'position',
            'phone_number',
            'email',
            'company',
        )


class EmployeeModelForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = (
            'position',
            'phone_number',
            'is_personal',
        )

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop('request_user', None)
        request_obj = kwargs.pop('request_obj', None)
        self.obj_instance = kwargs.get('instance', None)
        super(EmployeeModelForm, self).__init__(*args, **kwargs)
        self.fields['is_personal'].label = "Является сотрудником"

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not self.obj_instance:
            if Employee.objects.filter(username=username).exclude(id=self.instance.id).exists():
                raise forms.ValidationError("Это имя пользователя уже занято.")

        return username


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )

from django.forms.widgets import ClearableFileInput

class ImageField(forms.ClearableFileInput):
    template_name = "teams/custom_clearable_file_input.html"
    initial_text = 'Текущее изображение'
    input_text = 'Изменить'



class ProfileModelForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = (
            'phone_number',
            'birth_date',
            'profile_image',
        )
        widgets = {
            'profile_image': ImageField
        }



class EmailForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        to_user = kwargs.pop('to_user', None)
        super(EmailForm, self).__init__(*args, **kwargs)

        self.fields['subject'].label = "Тема"
        self.fields['message'].label = ''
        self.fields['from_email'].label = "Ваш email"
        self.fields['to_email'].label = "Получатель"

        self.fields['from_email'].widget.attrs['readonly'] = True
        self.fields['to_email'].widget.attrs['readonly'] = True
        self.fields['message'].widget.attrs['rows'] = 5
        self.fields['message'].widget.attrs['placeholder'] = 'Напишите сообщение...'

        self.fields['from_email'].widget.attrs['value'] = user
        self.fields['to_email'].widget.attrs['value'] = to_user
        self.fields['subject'].widget.attrs['placeholder'] = '...'

    to_email = forms.CharField()
    from_email = forms.CharField()
    subject = forms.CharField(max_length=30)
    message = forms.CharField(widget=forms.Textarea, max_length=500)

class EmailCompanyForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EmailCompanyForm, self).__init__(*args, **kwargs)

        self.fields['subject'].label = "Тема"
        self.fields['message'].label = ''
        self.fields['from_email'].label = "Ваш email"
        # self.fields['to_email'].label = "Получатель"

        self.fields['from_email'].widget.attrs['readonly'] = True
        # self.fields['to_email'].widget.attrs['readonly'] = True
        self.fields['message'].widget.attrs['rows'] = 5
        self.fields['message'].widget.attrs['placeholder'] = 'Напишите сообщение...'

        self.fields['from_email'].widget.attrs['value'] = user
        # self.fields['to_email'].widget.attrs['value'] = to_user
        self.fields['subject'].widget.attrs['placeholder'] = '...'

    from_email = forms.CharField()
    subject = forms.CharField(max_length=30)
    message = forms.CharField(widget=forms.Textarea, max_length=500)

class ContactSMSForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ContactSMSForm, self).__init__(*args, **kwargs)
        self.fields['message'].label = "Текст собщения"
        self.fields['message'].widget.attrs['title'] = "Заполните поле"

    message = forms.CharField(max_length=50)

class InventoryCompanyForm(forms.ModelForm):

    # def __init__(self, *args, **kwargs):
    #     pk = kwargs.pop('pk', None)
    #     super(InventoryCompanyForm, self).__init__(*args, **kwargs)

    #     self.fields['company'].label = "Компания"
    #     self.fields['company'].widget.attrs['value'] = pk
        # self.fields['company'].widget.attrs['readonly'] = True


    class Meta:
        model = InventoryCompany
        fields = (
            'employee',
            'pc',
            'pc_name',
            'comment',
        )

        # widgets = {
        #     'company': forms.HiddenInput
        # }