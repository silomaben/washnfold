from django.shortcuts import render, redirect, HttpResponse,get_object_or_404
from .models import Expense, Category,Order, Customer,PaymentMethod, ProductService,Transaction,Tranzaction
from .forms import ExpenseForm,TimeRangeForm
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
# from decimal import Decimal
from datetime import datetime,timedelta

# Create your views here.
def Home(request):
    return render(request,'home.html',{})

def ViewCustomer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    orders = Order.objects.filter(customer=customer)

    context = {
        'customer': customer,
        'orders': orders,
    }
    print(customer)

    return render(request, 'customer_detail.html',context)

def Customers(request):
    customers = Customer.objects.all()

    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        phoneNo = request.POST.get('phoneNo')
        email = request.POST.get('email')

        new_customer = Customer(
            first_name=first_name, 
            last_name=last_name, 
            phone_number=phoneNo,
            email=email,
            registration_date=timezone.now()  
        )
        
        new_customer.save()

        return redirect('customers') 

    return render(request,'customers.html',{'customers':customers})


def Store(request):
    productServices = ProductService.objects.all()
    return render(request,'store.html',{'store':productServices})

def Transactions(request):
    time_range = request.GET.get('time_range', 'today')

    form = TimeRangeForm(request.GET, initial={'time_range': time_range})

    if form.is_valid():
        custom_start_date = form.cleaned_data.get('custom_start_date')
        custom_end_date = form.cleaned_data.get('custom_end_date')
        
        end_date = timezone.now().date()
        start_date = None

        if time_range == 'this_year':
            start_date = datetime(end_date.year, 1, 1).date()
        elif time_range == 'this_month':
            start_date = datetime(end_date.year, end_date.month, 1).date()
        elif time_range == 'this_week':
            start_date = end_date - timedelta(days=end_date.weekday())
        elif time_range == 'today':
            start_date = end_date
        elif time_range == 'last_month':
            last_month = end_date.month - 1
            year = end_date.year

            if last_month < 1:
                last_month = 12
                year -= 1

            start_date = datetime(year, last_month, 1).date()
            end_date = start_date.replace(day=1) - timedelta(days=1)
        elif time_range == 'custom_range' and custom_start_date and custom_end_date:
            start_date = custom_start_date
            end_date = custom_end_date

        if start_date:
            transactions = Tranzaction.objects.filter(transaction_date__range=[start_date, end_date])
        else:
            transactions = Tranzaction.objects.all()

        total_income = sum(transaction.amount for transaction in transactions if transaction.type == 'income')
        total_expenses = sum(transaction.amount for transaction in transactions if transaction.type == 'expense')
        net_income = total_income - total_expenses

        context = {
            'transactions': transactions,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_income': net_income,
            'time_range': time_range,
            'form': form,
        }

        return render(request, 'transactions.html', context)

    transactions = Tranzaction.objects.filter(transaction_date=timezone.now().date())
    total_income = sum(transaction.amount for transaction in transactions if transaction.type == 'income')
    total_expenses = sum(transaction.amount for transaction in transactions if transaction.type == 'expense')
    net_income = total_income - total_expenses

    context = {
        'form': form,
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': net_income,
    }
    return render(request, 'transactions.html', context)

def get_customer_list(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == 'GET':
        name = request.GET.get('customer_name', '')
        phone_number = request.GET.get('customer_phoneNo', '')
        print('print:'+phone_number)
        # Create a query that filters customers by name or phone number
        customers = Customer.objects.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name) | Q(phone_number__exact=str(phone_number)))
        print('cust: '+str(customers))
        
        customer_list = [{'id': customer.id, 'first_name': customer.first_name, 'last_name': customer.last_name , 'phone': customer.phone_number} for customer in customers]
        return JsonResponse({'customers': customer_list})

def Orders(request):
  
    orders = Order.objects.select_related('customer')
    choices = PaymentMethod.objects.all().values_list('name','name')

    if request.method == 'POST':
        phone_number = request.POST.get('phoneNo')
        # customer_name = request.POST.get('customerName')
        status = request.POST.get('status')
        payment_method = request.POST.get('paymentMethod')
        amount = request.POST.get('amount')

        # Find the customer based on the provided phone number
        try:
            customer = Customer.objects.get(phone_number=phone_number)
        except Customer.DoesNotExist:
            # Handle the case where the customer does not exist or provide appropriate feedback
            return HttpResponse("Customer with this phone number does not exist")

        # Create a new order associated with the customer
        new_order = Order(
            customer=customer,  # Associate the order with the customer
            total_amount=amount,  # Use the appropriate field from your model
            status=status,
            payment_method=payment_method,
            order_date=timezone.now()  # You can set the order date as needed
        )
        
        new_order.save()

        

        return redirect('orders')
        
    return render(request,'orders.html',{'orders': orders, "choices":choices})



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

        return redirect('expenses')  

    else:
        form = ExpenseForm()

    return render(request,'expenses.html',{'expenses': expenses,'form':form,'choices':choice_list})
 
