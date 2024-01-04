from django.urls import path
from . import views



urlpatterns = [
    path('',views.Transactions,name='home'),
    path('expenses',views.Expenses,name='expenses'),
    path('orders',views.Orders,name='orders'),
    path('store',views.Store,name='store'),
    path('customers',views.Customers,name='customers'),
    path('customer/<int:customer_id>/',views.ViewCustomer,name='customer_detail'),
    path('receipt/<int:order_id>/',views.generate_pdf_receipt,name='receipt'),
    path('get_customer_list/', views.get_customer_list, name='get_customer_list'),
    path('ajax_order_data/', views.ajax_order_data, name='ajax_order_data'),
    path('ajax_daily_profits/', views.ajax_daily_profits, name='ajax_daily_profits'),
    path('ajax_yearly_profits/', views.ajax_yearly_profits, name='ajax_yearly_profits'),
    
]
