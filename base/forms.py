from django import forms
from .models import Expense,Category

choices = Category.objects.all().values_list('name','name')

choice_list = []

for item in choices:
    choice_list.append(item)


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'expense_date', 'category', 'payment_method']

        widgets = {
            'category': forms.Select(choices=choice_list,attrs={'class':'form-control'})
        }