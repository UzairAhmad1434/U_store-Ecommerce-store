from django.shortcuts import render
from .models import *
import json
import datetime
from .utils import cookieCart,cartData,guestUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def store(request):
	data=cartData(request)
	cartItems=data['cartItems']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)


def cart(request):
	data=cartData(request)
	cartItems=data['cartItems']
	order=data['order']
	items=data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data=cartData(request)
	cartItems=data['cartItems']
	order=data['order']
	items=data['items']
	
	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

@csrf_exempt
def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

@csrf_exempt
def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		
	else:
		customer, order = guestUser(request, data)
		
		
		 
			                          
	total = float(data['form']['total'])
	order.transaction_id = transaction_id
	order.complete = True
	order.save()
	
	ShippingAddress.objects.create(             
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            )

	return JsonResponse('Payment submitted..', safe=False)