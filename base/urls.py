from django.urls import path
from . import views



urlpatterns = [
    path('',views.Home,name='home'),
    path('expenses',views.Expenses,name='expenses'),
    path('orders',views.Orders,name='orders'),
]
