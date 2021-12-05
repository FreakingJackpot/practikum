from django.forms import ModelForm, Form, FileField

from .models import Request as RequestModel


class RequestForm(ModelForm):
    class Meta:
        model = RequestModel
        fields = ['phone', 'name', 'comment', ]


class ExcelImportForm(Form):
    excel_file = FileField()
