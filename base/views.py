from django.shortcuts import render, redirect, HttpResponse,get_object_or_404
from .models import Expense, Category,Order, Customer,PaymentMethod, ProductService,Transaction,Tranzaction
from .forms import ExpenseForm,TimeRangeForm
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
# from decimal import Decimal
from datetime import datetime,timedelta
from django.db.models import Count
from datetime import datetime, timedelta

from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Q

def Home(request):
    current_date = timezone.now().date()

    days_list = []
    customers_list = []
    total_orders_list = []
    for i in range(7):
        date_for_iteration = current_date - timezone.timedelta(days=i)
        
        orders_for_date = Order.objects.filter(order_date=date_for_iteration)
        total_orders_for_date = orders_for_date.count()

        day_of_week = date_for_iteration.strftime('%a')
        
        days_list.append(day_of_week)
        customers_list.append(orders_for_date.values('customer').distinct().count())
        total_orders_list.append(total_orders_for_date)

    # Reverse the lists to have them in the correct order (from oldest to newest)
    days_list.reverse()
    customers_list.reverse()
    total_orders_list.reverse()

    print(days_list)
    print(customers_list)
    print(total_orders_list)

    context = {
        'days_list': days_list,
        'customers_list': customers_list,
        'total_orders_list': total_orders_list,
    }
    return render(request, 'home.html', context)
  

    

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


def ajax_yearly_profits(request):
    current_date = datetime.now().date()
    current_year = current_date.year

    # Set the start_date to the beginning of the current year
    start_date = datetime(current_year, 1, 1).date()

    # Set the end_date to the end of the current year
    end_date = datetime(current_year, 12, 31).date()

    # Filter transactions for the current year
    transactions_current_year = Tranzaction.objects.filter(transaction_date__range=[start_date, end_date])

    # Create a list of all months in the current year
    all_months = [datetime(current_year, month, 1).strftime('%b') for month in range(1, 13)]

    # Initialize a dictionary to store monthly profits
    monthly_profits = {month: 0 for month in all_months}

    # Update profits based on transactions
    for transaction in transactions_current_year:
        month_key = transaction.transaction_date.strftime('%b')
        if transaction.type == 'income':
            monthly_profits[month_key] += transaction.amount
        elif transaction.type == 'expense':
            monthly_profits[month_key] -= transaction.amount

    # Prepare data for JsonResponse
    months_list = list(monthly_profits.keys())
    profits_list = list(monthly_profits.values())

    data = {
        'months_list': months_list,
        'profits_list': profits_list,
    }

    print(data)

    return JsonResponse(data)


def ajax_daily_profits(request):
   # Calculate the end date (today)
    end_date = timezone.now().date()

    # Calculate the start date (7 days ago)
    start_date = end_date - timedelta(days=7)

    # Filter transactions for the last 7 days
    transactions_last_7_days = Tranzaction.objects.filter(transaction_date__range=[start_date, end_date])

    # Calculate profits for each day
    daily_profits = []

    for i in range(7):
        date_for_iteration = end_date - timedelta(days=i)
        
        # Filter transactions for the current date
        transactions_for_date = transactions_last_7_days.filter(transaction_date=date_for_iteration)

        # Calculate total income and total expenses for the current date
        total_income_for_date = sum(transaction.amount for transaction in transactions_for_date if transaction.type == 'income')
        total_expenses_for_date = sum(transaction.amount for transaction in transactions_for_date if transaction.type == 'expense')

        # Calculate net income for the current date
        net_income_for_date = total_income_for_date - total_expenses_for_date

        # Append the result as a tuple to the daily_profits list
        daily_profits.append((date_for_iteration.strftime('%A')[0], net_income_for_date))

    # Reverse the lists before sending them in the AJAX response
    days_list = [day[0] for day in reversed(daily_profits)]
    daily_profits_list = [day[1] for day in reversed(daily_profits)]

    # Return the result as JSON
    data = {
        'days_list': days_list,
        'daily_profits_list': daily_profits_list,
    }

    return JsonResponse(data)

def ajax_order_data(request):
    current_date = timezone.now().date()
    days_list = []
    total_orders_list = []

    for i in range(7):
        date_for_iteration = current_date - timezone.timedelta(days=i)
        orders_for_date = Order.objects.filter(order_date=date_for_iteration)
        total_orders_for_date = orders_for_date.count()

        # Use strftime('%A')[0] to get the first letter of the day name
        day_of_week = date_for_iteration.strftime('%A')[0]

        days_list.append(day_of_week)
        total_orders_list.append(total_orders_for_date)

    # Reverse the lists before sending them in the AJAX response
    days_list.reverse()
    total_orders_list.reverse()

    data = {
        'days_list': days_list,
        'total_orders_list': total_orders_list,
    }

    return JsonResponse(data)

def get_customer_list(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == 'GET':
        name = request.GET.get('customer_name', '')
        phone_number = request.GET.get('customer_phoneNo', '')
        print('print:'+phone_number)
        # Create a query that filters customers by name or phone number
        customers = Customer.objects.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name) | Q(phone_number__exact=str(phone_number)))
        print('cust: '+str(customers))
        
        customer_list = [{'id': customer.id, 'first_name': customer.first_name, 'last_name': customer.last_name , 'phone': customer.phone_number} for customer in customers]

        # print(f"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee  :   {customer_list}")
        return JsonResponse({'customers': customer_list})

def Orders(request):
    orders = Order.objects.select_related('customer')
    choices = PaymentMethod.objects.all().values_list('name','name')

    if request.method == 'POST':
        phone_number = request.POST.get('phoneNo')
        status = request.POST.get('status')
        payment_method = request.POST.get('paymentMethod')
        cashAmount = request.POST.get('cashAmount')
        mpesaAmount = request.POST.get('mpesaAmount')
        description = request.POST.get('description')

        total_amount = int(cashAmount) + int(mpesaAmount)
        
        try:
            customer = Customer.objects.get(phone_number=phone_number)
        except Customer.DoesNotExist:
            return HttpResponse("Customer with this phone number does not exist")

        new_order = Order(
            customer=customer,  
            total_amount=total_amount,  
            cash_amount=cashAmount,  
            mpesa_amount=mpesaAmount,  
            status=status,
            payment_method=payment_method,
            order_date=timezone.now(),
            description = description  
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
 
