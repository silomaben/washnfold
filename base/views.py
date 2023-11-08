from django.shortcuts import render, redirect, HttpResponse
from .models import Expense, Category,Order, Customer,PaymentMethod, ProductService,Transaction,Tranzaction
from .forms import ExpenseForm
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from decimal import Decimal


# Create your views here.
def Home(request):
    return render(request,'home.html',{})
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
    all_transactions = Tranzaction.objects.all()

    total_income = Decimal('0.00')
    total_expenses = Decimal('0.00')

    for transaction in all_transactions:
        if transaction.type == 'income':
            total_income += transaction.amount
        elif transaction.type == 'expense':
            total_expenses += transaction.amount

    net_income = total_income - total_expenses

    context = {
        'transactions': all_transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': net_income,
    }

    # print(context)

    return render(request, 'transactions.html', context)
    # return render(request,'transactions.html',{'transactions':all_transactions})

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

        

        return redirect('home')
        
    return render(request,'orders.html',{'orders': orders, "choices":choices})

# def Orders1(request):
  
#     orders = Order.objects.select_related('customer')
#     choices = PaymentMethod.objects.all().values_list('name','name')

#     if request.method == 'POST':
#         phone_number = request.POST.get('phoneNo')
#         # customer_name = request.POST.get('customerName')
#         status = request.POST.get('status')
#         payment_method = request.POST.get('paymentMethod')
#         amount = request.POST.get('amount')

#         # Find the customer based on the provided phone number
#         try:
#             customer = Customer.objects.get(phone_number=phone_number)
#         except Customer.DoesNotExist:
#             # Handle the case where the customer does not exist or provide appropriate feedback
#             return HttpResponse("Customer with this phone number does not exist")

#         # Create a new order associated with the customer
#         new_order = Order(
#             customer=customer,  # Associate the order with the customer
#             total_amount=amount,  # Use the appropriate field from your model
#             status=status,
#             payment_method=payment_method,
#             order_date=timezone.now()  # You can set the order date as needed
#         )
        
#         new_order.save()

        

#         return redirect('home')
        
#     return render(request,'orders1.html',{'orders': orders, "choices":choices})



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
 

def Expenses1(request):

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

    return render(request,'expenses1.html',{'expenses': expenses,'form':form,'choices':choice_list})
 

