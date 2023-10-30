from django.db import models
from django.utils import timezone

# Customers table
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
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

    def __str__(self):
     return f'{self.description}'

# Orders Table
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')])
    payment_method = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        is_new_order = not self.pk  # Check if this is a new order being saved
        super(Order, self).save(*args, **kwargs)

        # If the order status is 'completed' and it's a new order, create an associated income record
        if self.status == 'completed' and is_new_order:
            Income.objects.create(
                order=self,
                payment_date=timezone.now(), # You can modify the payment_date as needed
                amount=self.total_amount,
                payment_method=self.payment_method
            )


# Income Table
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
