from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_docs, name='list_docs'),
    path('upload/', views.upload_doc, name='upload_doc'),
    path('analyse/', views.analyse_doc, name='analyse_doc'),
    path('get_text/', views.get_text, name='get_text'),
    path('delete/', views.delete_doc, name='delete_doc'),
    path('cart/', views.cart_list, name='cart_list'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/pay/<int:pk>/', views.cart_pay, name='cart_pay'),
]
