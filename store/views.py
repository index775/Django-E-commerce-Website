from django.shortcuts import render
from .models import * #use .models since they are in the same directory
from django.http import JsonResponse
import json
import datetime
from .utils import *

# Create your views here.
def store(request):
    data=cartData(request)
    cartItems=data['cartItems']
           
    products=Product.objects.all()
    context={'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):    
    data=cartData(request)
    cartItems=data['cartItems']
    order=data['order']
    items=data['items']

    context={'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):    
    data=cartData(request)
    cartItems=data['cartItems']
    order=data['order']
    items=data['items']
    # items=[]
    # order={'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
    # cartItems=order['get_cart_items']
    #everything is zero for a user who is not logged in 

    context={'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)
def updateItem(request):
    data=json.loads(request.body)
    productId=data['productId']
    action=data['action']

    print('Action:', action)
    print('productId:', productId)

    customer=request.user.customer
    product=Product.objects.get(id=productId)
    order, created=Order.objects.get_or_create(customer=customer, complete=False)
    
    orderItem, created=OrderItem.objects.get_or_create(order=order, product=product)

    if action=='add':
        orderItem.quantity=(orderItem.quantity + 1)
    elif action=='remove':
        orderItem.quantity=(orderItem.quantity - 1)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added to Cart', safe=False)

#from django.views.decorators.csrf import csrf_exempt
#@csrf_exempt
#This will still work but it is an insecure way
def processOrder(request):
    #print('Data:', request.body)
    transaction_id=datetime.datetime.now().timestamp()
    data=json.loads(request.body)

    if request.user.is_authenticated:
        customer=request.user.customer
        order, created=Order.objects.get_or_create(customer=customer, complete=False)
             
    else:
        customer, order=guestOrder(request, data)
    total=float(data['form']['total'])
    order.transaction_id=transaction_id

    if total==order.get_cart_total:
        order.complete=True
    order.save()

    if order.shipping==True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            county=data['shipping']['county'],
            streetname=data['shipping']['streetname'],
        )
    return JsonResponse('Payment was completed!', safe=False)