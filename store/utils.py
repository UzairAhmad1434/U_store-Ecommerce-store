from .models import *
import json

def cookieCart(request):
      items = []
      try:
        cart=json.loads(request.COOKIES['cart'])
      except:
        cart={}
        cartItems=0
        order = {'get_cart_total': 0, 'get_cart_items': 0,'shipping':False}
        for i in cart:
            try:
                cartItems=cart[i]['quantity']
                product=Product.objects.get(id=i)
                total=(product.price*cart[i]['quantity'])
                order['get_cart_items']=cart[i]['quantity']
                order['get_cart_total']=total
                item={
                  'product':{
                  'id':product.id,
                  'name':product.name,    
                  'price':product.price,
                  'imageURL':product.imageURL,
                  },
                  'quantity':cart[i]['quantity'],
                  'get_total':total, 
                  }
                items.append(item)
                if product.digital!=True:
                    order['shipping']=True
            except:
                pass
        return{'cartItems':cartItems,'order':order,'items':items}