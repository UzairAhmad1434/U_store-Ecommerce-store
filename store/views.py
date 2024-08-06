from django.shortcuts import render
from .models import *
import json
import datetime
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0,'shipping':False}
        cartItems=order['get_cart_items']
    products = Product.objects.all()
    context = {'products': products,'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items = []
        cartItems=0
        order = {'get_cart_total': 0, 'get_cart_items': 0,'shipping':False}

    context = {'items': items, 'order': order,'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items = []
        cartItems=0
        order = {'get_cart_total': 0, 'get_cart_items': 0,'shipping':False}

    context = {'items': items, 'order': order,'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

@csrf_exempt
def updateItem(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        productId = data.get('productId')
        action = data.get('action')

        customer = request.user.customer
        product = Product.objects.get(id=productId)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity += 1
        elif action == 'remove':
            orderItem.quantity -= 1

        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()

        cartItems = order.get_cart_items

        return JsonResponse({'cartItems': cartItems}, safe=False)
    
@csrf_exempt
def processOrder(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transaction_id = datetime.datetime.now().timestamp()

            if request.user.is_authenticated:
                customer = request.user.customer
                total = float(data['form']['total'])
                order, created = Order.objects.get_or_create(customer=customer, complete=False)
                order.transaction_id = transaction_id

                if total == order.get_cart_total:
                    order.complete = True
                    order.save()

                if order.shipping:
                    ShippingAddress.objects.create(
                        customer=customer,
                        order=order,
                        address=data['shipping']['address'],  # Ensure correct spelling
                        state=data['shipping']['state'],
                        city=data['shipping']['city'],
                        zipcode=data['shipping']['zipcode']
                    )

            return JsonResponse({"message": "Order processed"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON decoding error"}, status=400)
        except Exception as e:
            print(f"Error processing order: {e}")
            return JsonResponse({"error": "Internal server error"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)