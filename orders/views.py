from django.forms import ValidationError
from django.shortcuts import render, redirect
from django.contrib import messages
from products.models import Product # type: ignore
from orders.models import Order # type: ignore
from orders.models import OrderDetails # type: ignore
from .models import Payment
from django.utils import timezone

def add_to_cart(request):

 if 'pro_id' in request.GET and 'qty' in request.GET and 'price' in request.GET and request.user.is_authenticated and not request.user.is_anonymous:

    pro_id = request.GET['pro_id']
    qty = request.GET['qty']

    order = Order.objects.all().filter(user=request.user,is_finished=False)


    if not Product.objects.all().filter(id=pro_id).exists():
          return redirect('products')
    pro = Product.objects.get(id=pro_id)

    if order:
      #messages.success(request, 'يوجد طلب قديم ')
      old_order = Order.objects.get(user=request.user,is_finished=False)
      if OrderDetails.objects.all().filter(order=old_order,product=pro).exists():
         orderdetails = OrderDetails.objects.get(order=old_order,product=pro)
         orderdetails.quantity += int(qty)
         orderdetails.save()
      else:
          orderdetails = OrderDetails.objects.create( product=pro, order=old_order, price=pro.price, quantity=qty)
      messages.success(request, 'Was added to cart for old order')
    else:
      #messages.success(request, ' هنا سوف يتم عمل طلب جديد ')
      new_order = Order()
      new_order.user = request.user
      new_order.order_date = timezone.now()
      new_order.is_finished = False
      new_order.save()
      orderdetails = OrderDetails.objects.create(product=pro,order=new_order, price=pro.price, quantity=qty)
      messages.success(request, 'Was added to cart for new order ')

    return redirect('/products/' + request.GET['pro_id'])
 else:
      if 'pro_id' in request.GET:
          messages.error(request, 'You must be logged in')
          return redirect('/products/' + request.GET['pro_id'])
      else:
          return redirect('index')
       
 
def cart(request):
   context = None
   if request.user.is_authenticated and not request.user.is_anonymous:
      if Order.objects.all().filter(user=request.user, is_finished=False):
         order = Order.objects.get(user=request.user,is_finished=False) 
         orderdetails = OrderDetails.objects.all().filter(order=order)
         total = 0 
         for sub in orderdetails:
            total += sub.price * sub.quantity
         context = {
             'order':order,
             'orderdetails':orderdetails,
             'total':total,
          }  
   return render(request, 'orders/cart.html', context)

def remove_from_cart(request, orderdetails_id):
   if request.user.is_authenticated and not request.user.is_anonymous and orderdetails_id:
      orderdetails = OrderDetails.objects.get(id=orderdetails_id)
      if orderdetails.order.user.id==request.user.id:

         orderdetails.delete()
   return redirect('cart')   

def add_qty(request, orderdetails_id):
   if request.user.is_authenticated and not request.user.is_anonymous and orderdetails_id:
      orderdetails = OrderDetails.objects.get(id=orderdetails_id)
      if orderdetails.order.user.id==request.user.id:

         orderdetails.quantity += 1
         orderdetails.save()
   return redirect('cart')

def sub_qty(request, orderdetails_id):
   if request.user.is_authenticated and not request.user.is_anonymous and orderdetails_id:
      orderdetails = OrderDetails.objects.get(id=orderdetails_id)
      if orderdetails.order.user.id==request.user.id:

        if orderdetails.quantity>1:
           orderdetails.quantity -= 1
           orderdetails.save()
   return redirect('cart')



def payment(request):
    context = None
    if request.method == 'POST' and 'btnpayment' in request.POST:
        ship_address = request.POST.get('ship_address')
        ship_phone = request.POST.get('ship_phone')
        card_number = request.POST.get('card_number')
        expire = request.POST.get('expire')
        security_code = request.POST.get('security_code')
        
        if request.user.is_authenticated and not request.user.is_anonymous:
            if Order.objects.filter(user=request.user, is_finished=False).exists():
                order = Order.objects.get(user=request.user, is_finished=False)
                
                # إنشاء كائن الدفع بدون حفظه أولاً
                payment = Payment(
                    order=order,
                    shipment_address=ship_address,
                    shipment_phone=ship_phone,
                    card_number=card_number,
                    expire=expire,
                    security_code=security_code
                )
                
                try:
                    # التحقق من الصحة قبل الحفظ
                    payment.full_clean()
                    payment.save()
                    order.is_finished = True
                    order.save()
                    messages.success(request, 'Your order is finished')
                    return redirect('show_orders')
                except ValidationError as e:
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                    return redirect('payment')
    
    # معالجة طلب GET
    if request.user.is_authenticated and not request.user.is_anonymous:
        if Order.objects.filter(user=request.user, is_finished=False).exists():
            order = Order.objects.get(user=request.user, is_finished=False)
            orderdetails = OrderDetails.objects.filter(order=order)
            total = sum(sub.price * sub.quantity for sub in orderdetails)
            context = {
                'order': order,
                'orderdetails': orderdetails,
                'total': total,
            }
    
    return render(request, 'orders/payment.html', context)
  


def show_orders(request):
   context = None
   all_orders = None
   if request.user.is_authenticated and not request.user.is_anonymous:
      all_orders = Order.objects.all().filter(user=request.user)
      if all_orders:
         for x in all_orders:
            order = Order.objects.get(id=x.id) 
            orderdetails = OrderDetails.objects.all().filter(order=order)
            total = 0 
            for sub in orderdetails:
               total += sub.price * sub.quantity
               x.total = total
               x.items_count = orderdetails.count
   context = {'all_orders':all_orders}
   return render(request, 'orders/show_orders.html',context)
