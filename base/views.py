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

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle,TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.platypus import Image



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

    # print(days_list)
    # print(customers_list)
    # print(total_orders_list)

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
    # print(customer)

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

        # if start_date:
        #     transactions = Tranzaction.objects.filter(transaction_date__range=[start_date, end_date])
        # else:
        #     transactions = Tranzaction.objects.all()

        if start_date:
            transactions = Tranzaction.objects.filter(transaction_date__range=[start_date, end_date]).order_by('-transaction_date')
        else:
            transactions = Tranzaction.objects.all().order_by('-transaction_date')

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

    transactions = Tranzaction.objects.filter(transaction_date=timezone.now().date()).order_by('-transaction_date')
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

    start_date = datetime(current_year, 1, 1).date()
    end_date = datetime(current_year, 12, 31).date()

    transactions_current_year = Tranzaction.objects.filter(transaction_date__range=[start_date, end_date])
    all_months = [datetime(current_year, month, 1).strftime('%b') for month in range(1, 13)]

    monthly_profits = {month: 0 for month in all_months}

    for transaction in transactions_current_year:
        month_key = transaction.transaction_date.strftime('%b')
        if transaction.type == 'income':
            monthly_profits[month_key] += transaction.amount
        elif transaction.type == 'expense':
            monthly_profits[month_key] -= transaction.amount

    months_list = list(monthly_profits.keys())
    profits_list = list(monthly_profits.values())

    data = {
        'months_list': months_list,
        'profits_list': profits_list,
    }

    return JsonResponse(data)


def ajax_daily_profits(request):
    selected_date = request.GET.get("selected_date")

    if selected_date:
        selected_date = timezone.datetime.strptime(selected_date, "%Y-%m-%d").date()
    else:
        selected_date = timezone.now().date()

    start_date = selected_date - timedelta(days=selected_date.weekday())

    transactions_for_week = Tranzaction.objects.filter(
        transaction_date__range=[start_date, start_date + timedelta(days=6)]
    )

    weekly_profits = []

    for i in range(7):
        date_for_iteration = start_date + timedelta(days=i)

        transactions_for_date = transactions_for_week.filter(
            transaction_date=date_for_iteration
        )

        total_income_for_date = sum(
            transaction.amount for transaction in transactions_for_date if transaction.type == 'income'
        )
        total_expenses_for_date = sum(
            transaction.amount for transaction in transactions_for_date if transaction.type == 'expense'
        )

        net_income_for_date = total_income_for_date - total_expenses_for_date

        print(date_for_iteration)
        print(net_income_for_date)

        weekly_profits.append((date_for_iteration.strftime('%A')[0], int(net_income_for_date)))

    weekly_profits = list(reversed(weekly_profits))

    # Return the result as JSON
    data = {
        'weekly_profits': weekly_profits,
    }

    print(data)

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

        customers = Customer.objects.all()

        if phone_number:
            customers = customers.filter(Q(phone_number__icontains=phone_number))

        if name:
            customers = customers.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))

        customer_list = [{'id': customer.id, 'first_name': customer.first_name, 'last_name': customer.last_name, 'phone': customer.phone_number} for customer in customers]
        return JsonResponse({'customers': customer_list})
    
def Orders(request):
    choices = PaymentMethod.objects.all().values_list('name', 'name')
    orders = Order.objects.filter(order_date__range=(timezone.now().date(),timezone.now().date())).select_related('customer')

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
            orders = Order.objects.filter(order_date__range=[start_date, end_date]).select_related('customer').order_by('-order_date')
        else:
            orders = Order.objects.select_related('customer').order_by('-order_date')

        status_filter = request.GET.get('status')
        
        if status_filter:
            orders = orders.filter(status=status_filter)

    if request.method == 'POST':
        order_id_to_delete = request.POST.get('order_id')
        delete_action = request.POST.get('delete_action')

        if delete_action:
            order_to_delete = get_object_or_404(Order, id=order_id_to_delete)
            order_to_delete.delete()
            return redirect('orders')
        
        order_id_to_edit = request.POST.get('submitOrder')

        if order_id_to_edit:
            # Editing an existing order
            order_to_edit = get_object_or_404(Order, id=order_id_to_edit)
        else:
            # Creating a new order
            phone_number = request.POST.get('phoneNo')

            if not phone_number:
                return HttpResponse("Phone number is required for creating a new order.")

            try:
                customer = Customer.objects.get(phone_number=phone_number)
            except Customer.DoesNotExist:
                return HttpResponse("Customer with this phone number does not exist")

            order_to_edit = Order(customer=customer)

        # Extract other form data
        status = request.POST.get('status')
        payment_method = request.POST.get('paymentMethod')
        cashAmount = request.POST.get('cashAmount')
        mpesaAmount = request.POST.get('mpesaAmount')
        description = request.POST.get('description')

        # Process amounts
        cashAmount = float(cashAmount) if cashAmount else 0
        mpesaAmount = float(mpesaAmount) if mpesaAmount else 0
        total_amount = cashAmount + mpesaAmount

        # Update or create the order
        order_to_edit.total_amount = total_amount
        order_to_edit.cash_amount = cashAmount
        order_to_edit.mpesa_amount = mpesaAmount
        order_to_edit.status = status
        order_to_edit.payment_method = payment_method
        order_to_edit.order_date = timezone.now()
        order_to_edit.description = description

        order_to_edit.save()

        return redirect('orders')
    
    context = {
        'form': form,
        'orders': orders, 
        "choices": choices
    }

    return render(request, 'orders.html', context)

def Expenses(request):

    choices = Category.objects.all().values_list('name','name')

    choice_list = []

    for item in choices:
        choice_list.append(item)

    expenses = Expense.objects.all().order_by('-expense_date')

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
 

def generate_pdf_receipt(request, order_id):
    # Fetch the order details from the database
    order = Order.objects.get(pk=order_id)

    # Create a PDF response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=receipt_{order_id}.pdf'

    # Define the custom width for the receipt (adjust as needed)
    receipt_width = 3.14 * 72  # 1 inch = 72 points
     # Split the orders.description string
    description_data = order.description.split(',')

    
    # Determine the minimum number of rows
    min_rows = 5

    # Ensure there are enough items to meet the minimum rows
    while len(description_data) < min_rows:
        description_data.append('')  # Add empty items if needed

    min_receipt_height = 5 * 79  # 5 inches as the minimum height
    height_increment = 0.3 * 72  # Half inch for every extra record
    dynamic_receipt_height = min_receipt_height + (len(description_data) - min_rows) * height_increment

    doc = SimpleDocTemplate(response, pagesize=(receipt_width, dynamic_receipt_height), title=f'Receipt for {order.customer}',leftMargin=10, rightMargin=10, topMargin=1)
    styles = getSampleStyleSheet()


    # Business information
    business_logo_path = "static\dashboard\img\washnfold.png"
    business_phone = "0724-244-442"
    business_location = "Lanet, Nakuru"

    # Add business name and logo
    elements = []
    logo = Image(business_logo_path, width=150, height=53.55)
    logo.hAlign = 'CENTER'  # Align the image to the center horizontally
    elements.append(logo)


    # Add business information
    businessTitle = ParagraphStyle(styles['Normal'], alignment=TA_CENTER,spaceAfter=5)
    businessTitle.fontSize = 14
    elements.append(Paragraph(f"Laundry Receipt", ParagraphStyle(name='CenterTextWithPadding', parent=styles['Normal'], alignment=TA_CENTER, spaceBefore=10)))
    elements.append(Paragraph(f"<b>Joe Wash N' Fold</b>", businessTitle))
    elements.append(Paragraph(f"{business_phone}", ParagraphStyle(styles['Normal'], alignment=TA_CENTER,spaceAfter=2)))
    elements.append(Paragraph(f"{business_location}", ParagraphStyle(styles['Normal'], alignment=TA_CENTER,spaceAfter=2)))

    # Add content to the PDF
    
    

    # Customer details
    elements.append(Paragraph(f"{order.order_date}", ParagraphStyle(name='CenterTextWithPadding', parent=styles['Normal'], alignment=TA_CENTER,spaceAfter=10)))
    elements.append(Paragraph(f"<b>Prepared for:</b> {order.customer}", ParagraphStyle(name='spaceAfterTxt', parent=styles['Normal'],spaceAfter=15)))


    # Create a table with the split data
    table_data = [['#', 'Item', '✔']]
    for i, item in enumerate(description_data, start=1):
        if item.strip():  # Only add numbers to non-empty items
            table_data.append([i, item.strip(), ''])  # Using the checkmark symbol, adjust as needed
        else:
            table_data.append(['', item.strip(), ''])  # Add empty row without numbers


    # Create the table
    table = Table(table_data, colWidths=[20, 150, 20], hAlign='LEFT')

    # Apply styles to the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # Add the table to elements
    elements.append(table)

    # Total Amount
    elements.append(Paragraph(f"<b>Total Amount:</b> {order.total_amount}", ParagraphStyle(styles['Normal'], spaceBefore=10)))


    # Build the PDF and return the response
    doc.build(elements)

    return response