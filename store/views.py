from django.shortcuts import render
from .models import *
import json
import datetime
from .utils import cookieCart,cartData
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def store(request):
    data=cartData(request)
    cartItems=data['cartItems']
    products = Product.objects.all()
    context = {'products':products,'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    data=cartData(request)
    cartItems=data['cartItems']
    order=data['order']
    items=data['items']
    context = {'items': items, 'order': order,'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data=cartData(request)
    cartItems=data['cartItems']
    order=data['order']
    items=data['items']
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

        cartItems = order.get_cart_items()

        return JsonResponse({'cartItems': cartItems}, safe=False)
    


@csrf_exempt
def processOrder(request):
    if request.method == 'POST': 
        try:
            data = json.loads(request.body)
            transaction_id = datetime.datetime.now().timestamp()

            if request.user.is_authenticated:
                customer = request.user.customer
                order, created = Order.objects.get_or_create(customer=customer, complete=False)
            total = float(data['form']['total'])
            order.transaction_id = transaction_id
            order.save()

            if total == float(order.get_cart_total):
                order.complete = True
            order.save()
            order.shipping==True
            if order.shipping:
                ShippingAddress+=ShippingAddress.objects.create(
                    customer=customer,
                    order=order,
                    address=data['shipping']['address'], 
                    state=data['shipping']['state'],
                    city=data['shipping']['city'],
                    zipcode=data['shipping']['zipcode']
                )
            else:
                print('User not logged in')
                print('Cookies:', request.COOKIES)
                name = data['form']['email']
                email = data['form']['email']

                cookieData = cookieCart(request)
                items = cookieData['items']

                customer, created = Customer.objects.get_or_create(email=email)

                if not customer:
                    print('No customer created')
                customer.save()

                order = Order.objects.create(customer=customer, complete=False)

                for item in items:
                    product = Product.objects.get(id=item['product']['id'])
                    OrderItem.objects.create(product=product, order=order, quantity=item['quantity'])

            

            return JsonResponse({"message": "Order processed"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON decoding error"}, status=400)
        except Exception as e:
            print(f"Error processing order: {e}")
            return JsonResponse({"error": "Internal server error"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)