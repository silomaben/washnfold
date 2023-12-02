from django.db import models
from  django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, null=True , on_delete=models.CASCADE )
    contact = models.CharField(max_length=100)
    date_of_hire = models.DateField()
    profile_pic = models.ImageField(null=True,blank=True,upload_to="images/profile/")

# Customers table
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15,unique=True)
    email = models.EmailField(null=True)
    # address = models.TextField()
    loyalty_points = models.IntegerField(default=0)
    registration_date = models.DateField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

# Expenses Table
class Expense(models.Model):
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()
    category = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        is_new_expense = not self.pk  # Check if this is a new order being saved
        super(Expense, self).save(*args, **kwargs)

        # If the order status is 'completed' and it's a new order, create an associated income record
        if is_new_expense:
            expense = Expense.objects.get(pk=1)
            transaction = Tranzaction(
                transaction_date=self.expense_date,
                amount=self.amount,
                content_object=expense,  # Associate with an Order
                type='expense'  # Or 'income' as needed
            )
            transaction.save()

    def __str__(self):
     return f'{self.description}'

# Orders Table
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')])
    payment_method = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cash_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mpesa_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    def save(self, *args, **kwargs):
        is_new_order = not self.pk
        super(Order, self).save(*args, **kwargs)

        if self.status == 'completed':
            income = Income.objects.create(
                order=self,
                payment_date=timezone.now(), 
                amount=self.total_amount,
                payment_method=self.payment_method
            )

            income.save()

            loyalty_points = int(self.total_amount / 1000)
            self.customer.loyalty_points += loyalty_points
            self.customer.save()
            
        if is_new_order:
            transaction = Tranzaction(
                transaction_date=self.order_date,
                amount=self.total_amount,
                content_object=self, 
                type='income'
            )
            transaction.save()
           



class Income(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)



# Products/Services Table
class ProductService(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    category = models.CharField(max_length=50)
    stock_quantity = models.PositiveIntegerField(default=0)

# Users Table
class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    hire_date = models.DateField()
    position = models.CharField(max_length=50)

# Transactions Table
class Transaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=[('income', 'Income'), ('expense', 'Expense')])
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class Tranzaction(models.Model):
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Generic Foreign Key fields to reference Order and Expense
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    type = models.CharField(
        max_length=10,
        choices=[('income', 'Income'), ('expense', 'Expense')]
    )

# Payment Methods Table
class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)

# Categories Table
class Category(models.Model):
    name = models.CharField(max_length=50)

# Discounts Table
class Discount(models.Model):
    name = models.CharField(max_length=100)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
