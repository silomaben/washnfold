from django.urls import path
from . import views



urlpatterns = [
    path('',views.Home,name='home'),
    path('expenses',views.Expenses,name='expenses'),
    path('expenses1',views.Expenses1,name='expenses1'),
    path('orders',views.Orders,name='orders'),
    path('store',views.Store,name='store'),
    path('customers',views.Customers,name='customers'),
    path('transactions',views.Transactions,name='transactions'),
    path('get_customer_list/', views.get_customer_list, name='get_customer_list'),
    # path('orders1',views.Orders1,name='orders1'),
]
