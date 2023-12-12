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

        # forms.py




class TimeRangeForm(forms.Form):
    time_range_choices = [
        ('today', 'Today'),
        ('all_time', 'All Time'),
        ('this_year', 'This Year'),
        ('this_month', 'This Month'),
        ('this_week', 'This Week'),
        ('custom_range', 'Custom Range'),
    ]

    status_choices = [
        ('', 'All(status)'),  # Empty string represents all statuses
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    time_range = forms.ChoiceField(choices=time_range_choices, label='Select Time Range')
    custom_start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Start Date'
    )
    custom_end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='End Date'
    )

    status = forms.ChoiceField(choices=status_choices, required=False, label='Select Status')

