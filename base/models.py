from django.db import models
from  django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
import uuid
from decimal import Decimal

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
    email = models.EmailField(null=True, blank=True)
    # address = models.TextField()
    loyalty_points =models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    registration_date = models.DateField()
    profile_pic = models.ImageField(null=True,blank=True,upload_to="images/profile/customer/")

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

# Expenses Table
class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()
    category = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        is_new_expense = not self.pk
        super(Expense, self).save(*args, **kwargs)
        transaction = Tranzaction(
            transaction_date=self.expense_date,
            amount=self.amount,
            content_object=self,  # Associate with an Order
            type='expense'  # Or 'income' as needed
        )
        transaction.save()

            
    def delete(self, *args, **kwargs):
        # Delete associated Tranzaction instances
        Tranzaction.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id
        ).delete()

        # Now delete the Order instance
        super(Expense, self).delete(*args, **kwargs)

    

    def __str__(self):
     return f' {self.amount}  -- {self.expense_date}-- {self.description}'

# Orders Table
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')])
    payment_method = models.CharField(max_length=50,null=True)
    description = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cash_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mpesa_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    
    def delete(self, *args, **kwargs):
        # Delete associated Tranzaction instances
        Tranzaction.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id
        ).delete()

        # Now delete the Order instance
        super(Order, self).delete(*args, **kwargs)

    

    def save(self, *args, **kwargs):
        is_new_order = not self.pk
        super(Order, self).save(*args, **kwargs)

        # Check if the order is marked as completed
        if self.status == 'completed':
            # Create a new Tranzaction instance
            transaction = Tranzaction(
                transaction_date=self.order_date,
                amount=self.total_amount,
                content_object=self,
                type='income'
            )
            transaction.save()

            # Additional logic when the order is marked as completed
            income = Income.objects.create(
                order=self,
                payment_date=timezone.now(),
                amount=self.total_amount,
                payment_method=self.payment_method
            )
            income.save()

            loyalty_points = Decimal(self.total_amount) / Decimal(1000.0)
            self.customer.loyalty_points += loyalty_points
            self.customer.save()

        # Check if the order status is updated to something other than completed
        elif not is_new_order and self.status != 'completed':
            # Delete existing Tranzaction instances
            Tranzaction.objects.filter(
                content_type=ContentType.objects.get_for_model(Order),
                object_id=self.id
            ).delete()
            
        
           



class Income(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=[('income', 'Income'), ('expense', 'Expense')])
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class Tranzaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Generic Foreign Key fields to reference Order and Expense
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
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
