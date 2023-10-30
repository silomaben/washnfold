from django.shortcuts import render, redirect
from .models import Expense, Category,Order
from .forms import ExpenseForm


# Create your views here.
def Home(request):
    return render(request,'home.html',{})
# Create your views here.
def Orders(request):
    # Query orders and include customer information using select_related
    orders = Order.objects.select_related('customer')
    return render(request,'orders.html',{'orders': orders})



def Expenses(request):

    choices = Category.objects.all().values_list('name','name')

    choice_list = []

    for item in choices:
        choice_list.append(item)

    expenses = Expense.objects.all()

    if request.method == 'POST':
        description = request.POST.get('description')
        expense_date = request.POST.get('expenseDate')
        category = request.POST.get('category')
        payment_method = request.POST.get('paymentMethod')
        amount = request.POST.get('amount')
        # Extract other form fields as needed

        # Create a new instance of YourModel and save it
        expense = Expense(description=description, amount=amount, expense_date=expense_date, category=category, payment_method=payment_method)
        expense.save()

        return redirect('home')  # Redirect to a success page or any other desired URL

    else:
        form = ExpenseForm()

    return render(request,'expenses.html',{'expenses': expenses,'form':form,'choices':choice_list})
 

