from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.db import IntegrityError
from django.utils import timezone
from datetime import date, timedelta, datetime
import calendar
import json
import requests
import base64
from django.conf import settings
import logging
import os
# Create your views here.

# ! FACE ID:
def get_append_face_id(request, user_id):
    error = None
    context = {}
    user =User.objects.filter(id=user_id).first()
    context['user']=user
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data.get('image')

        # Tách phần header của base64 (e.g., "data:image/png;base64,")
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]  # Lấy phần mở rộng (e.g., png, jpg)

        img_data = base64.b64decode(imgstr)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        file_name = f'face_{user_id}_{timestamp}.{ext}'

        # Lưu ảnh tạm thời
        temp_file_path = os.path.join(settings.MEDIA_ROOT, 'face_images', file_name)
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        with open(temp_file_path, 'wb') as f:
            f.write(img_data)
        # Lưu vào model User_Face
        face_image = User_Face.objects.create(
            user=user,
            face=f'face_images/{file_name}'  # Đường dẫn tương đối
        )
        return JsonResponse({
            'status': 'success',
            'message': f'Ảnh {file_name} đã được lưu cho user {user_id}',
            'image_id': face_image.id
        }, status=200)
    context['error']=error
    return render(request, 'face_id/append.html', context)

def get_faces(request, user_id):
    if request.method =='GET':
        user = User.objects.filter(id=user_id).first()
        faces = User_Face.objects.filter(user=user)
        face_urls = [{'url': request.build_absolute_uri(face.face.url)} for face in faces if face.face]
        return JsonResponse(face_urls, safe=False)

def get_face_identification(request, user_id):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    context['user']=user
    cart_items = Cart.objects.filter(user=user)
    total = sum(cart.get_total() for cart in cart_items)
    context['total']="{:,.0f} VND".format(total)
    if request.method =='POST':
        if user.balance < total:
            error = 'Not enough balance'
            context['error']=error
            return render(request, 'customer/identification.html', context)
        user.balance -= total
        user.save()
        order = Order.objects.create(user=user)
        for cart in cart_items:
            seller = cart.product.seller
            seller.balance += cart.get_total()
            seller.save()
            product = cart.product
            product.quantity -= cart.quantity
            product.save()
            order_product = Order_Product.objects.create(
                order = order,
                product = product,
                quantity = cart.quantity,
            )
            cart.delete() 
        return JsonResponse({})
    context['error']=error
    return render(request, 'face_id/identification.html', context)



# ! CHAT BOT:
def send_message(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method =='POST':
        data = json.loads(request.body)
        message = data.get('message','Hi')
        rasa_response = requests.post(
            'http://localhost:5005/webhooks/rest/webhook',
            json={'sender': user.username, 'message': message}
        )
        response_data = rasa_response.json()
        bot_message = response_data[0]['text'] if response_data else "Sorry, I didn't understand."
        Chat.objects.create(
            user = user,
            request = message,
            response = bot_message
        )
        return JsonResponse({
            'request':message,
            'response':bot_message
        })
    return JsonResponse({})

# ! Account:
def get_login(request):
    error = None
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = User.objects.filter(username=username, password=password).first()
        if user:
            return redirect('get_home_customer', user_id = user.id)
    return render(request,'account/login.html',context)

def get_register(request):
    error = None
    context = {}
    addresses = Address.objects.all()
    context['addresses'] = addresses
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')
        if password != confirm_password:
            error = 'Passwords do not match'
            context['error'] = error
            return render(request,'account/register.html',context)
        name = request.POST.get('name')
        address_id = int(request.POST.get('address'))
        address_number = request.POST.get('address_number')
        phone = request.POST.get('phone_number')
        try:
            address = Address.objects.get(id=address_id)
            user = User.objects.create(username=username, password=password, name=name, address=address, address_number=address_number, phone=phone)
            return redirect('get_login')
        except IntegrityError:
            error = 'Username already exists'
    return render(request,'account/register.html',context)

def get_setting(request, user_id):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    context['user'] = user
    return render(request,'account/setting.html',context)

# ! CUSTOMER:

def dec_quantity_in_cart(request, cart_id, change):
    if request.method == 'POST':
        cart = Cart.objects.filter(id=cart_id).first()
        new_quantity = cart.quantity - change
        # Kiểm tra số lượng không âm
        if new_quantity < 1:
            return JsonResponse({
                'success': False,
                'error': 'Quantity cannot be less than 1, you can remove it',
                'error_message' : 'Quantity cannot be less than 1, you can remove it',
            }, status=400)
        # Cập nhật status
        cart.quantity = new_quantity
        cart.save()
        return JsonResponse({
            'success': True,
            'new_quantity': new_quantity,
        })

def inc_quantity_in_cart(request, cart_id, change):
    if request.method == 'POST':
        cart = Cart.objects.filter(id=cart_id).first()
        new_quantity = cart.quantity + change
        # Kiểm tra số lượng không âm
        if new_quantity > cart.product.quantity:
            return JsonResponse({
                'success': False,
                'error': 'Limit quantity',
                'error_message': 'limit quantity',
            }, status=400)
        # Cập nhật status nếu cần
        cart.quantity = new_quantity
        cart.save()
        return JsonResponse({
            'success': True,
            'new_quantity': new_quantity,
        })

def delete_cart(request, user_id, product_id):
    if request.method == 'DELETE':
        user = User.objects.filter(id=user_id).first()
        product = Product.objects.filter(id=product_id).first()
        cart = Cart.objects.filter(user=user, product=product).first()
        cart.delete()
        return JsonResponse({
            'success':True,
            'message':'Remove successfully',
        })

def add_to_cart(request, user_id, product_id):
    if request.method == 'POST':
        user = User.objects.filter(id=user_id).first()
        product = Product.objects.filter(id=product_id).first()
        cart_check = Cart.objects.filter(user=user, product=product).first()
        if cart_check:
            cart_check.quantity += 1
            cart_check.save()
            return JsonResponse({
                'success': True,
                'message': f'Product quantity updated in cart',
                'cart_id': cart_check.id,
            })
        else:
            cart = Cart.objects.create(user=user, product=product, quantity=1)
            return JsonResponse({
                'success': True,
                'message': 'Product added to cart successfully',
                'cart_id': cart.id,
            })

def like_product(request, user_id, product_id):
    if request.method == 'POST':
        user = User.objects.filter(id=user_id).first()
        product = Product.objects.filter(id=product_id).first()
        favorite_check = FavoriteList.objects.filter(user=user, product=product).first()
        if favorite_check:
            favorite_check.delete()
            return JsonResponse({
                'success': True,
                'message': 'Product removed from favorites',
                'button_text': 'Like',
            })
        else:
            favorite = FavoriteList.objects.create(user=user, product=product)
            return JsonResponse({
                'success': True,
                'message': 'Product added to favorites successfully',
                'favorite_id': favorite.id,
                'button_text': 'Unlike',
            })

def get_history(request, user_id):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    context['user']=user
    return render(request, 'customer/history.html', context)

def get_identification(request, user_id):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    context['user'] = user
    cart_items = Cart.objects.filter(user=user)
    total = sum(cart.get_total() for cart in cart_items)
    context['total']="{:,.0f} VND".format(total)
    if request.method =='POST':
        password = request.POST.get('password')
        if password != user.password:
            error = 'Wrong password'
            context['error']=error
            return render(request, 'customer/identification.html', context)
        if user.balance < total:
            error = 'Not enough balance'
            context['error']=error
            return render(request, 'customer/identification.html', context)
        user.balance -= total
        user.save()
        order = Order.objects.create(user=user)
        for cart in cart_items:
            seller = cart.product.seller
            seller.balance += cart.get_total()
            seller.save()
            product = cart.product
            product.quantity -= cart.quantity
            product.save()
            order_product = Order_Product.objects.create(
                order = order,
                product = product,
                quantity = cart.quantity,
            )
            cart.delete() 
        return redirect('get_history', user_id)
    context['error']=error
    return render(request, 'customer/identification.html', context)

def get_payment(request, user_id):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    context['user'] = user
    cart_items = Cart.objects.filter(user=user)
    context['total']="{:,.0f} VND".format(sum(cart.get_total() for cart in cart_items))
    carts = []
    for cart in cart_items:
        image = Product_Image.objects.filter(product=cart.product).first()
        carts.append({
            'cart': cart,
            'image': image,
        })
    context['carts'] = carts
    context['error'] = error
    return render(request,'customer/payment.html',context)

def get_cart(request, user_id):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    context['user'] = user
    cart_items = Cart.objects.filter(user=user)
    carts = []
    for cart in cart_items:
        image = Product_Image.objects.filter(product=cart.product).first()
        carts.append({
            'cart': cart,
            'image': image,
        })
    context['carts'] = carts
    context['error'] = error
    return render(request,'customer/cart.html',context)

def get_favorite_list(request, user_id):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    context['user'] = user
    favorite_items = FavoriteList.objects.filter(user=user)
    favorite_list = []
    for favorite in favorite_items:
        favorite_list.append({
            'id': favorite.product.id,
            'image': Product_Image.objects.filter(product=favorite.product).first(),
            'name': favorite.product.name,
            'price': favorite.product.price,
        })
    context['favorite_list'] = favorite_list
    context['error'] = error
    return render(request,'customer/favorite_list.html',context)

def get_product_view_customer(request,user_id, product_id):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    context['user'] = user
    product = Product.objects.filter(id=product_id).first()
    images = Product_Image.objects.filter(product=product)
    context['product'] = {
        'id': product.id,
        'images':images,
        'name':product.name,
        'price':product.price,
        'description': product.description,
        'category': product.category.name,
        'like': FavoriteList.objects.filter(user=user, product=product),
        'seller_id': product.seller.id,
        'seller_name': product.seller.name,
        'order_product_list' : Order_Product.objects.filter(product=product)
    }
    return render(request,'customer/product_view.html',context)

def get_shop(request, user_id, seller_id):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    seller = User.objects.filter(id=seller_id).first()
    context['user'] = user
    products = Product.objects.exclude(seller=user).filter(seller=seller,status='available')[:20]
    product_data_list = []
    for product in products:
        image = Product_Image.objects.filter(product=product).first()
        like = FavoriteList.objects.filter(user=user, product=product).first()
        product_data = {
            'product': product,
            'image': image,
            'like': like if like else None,
        }
        product_data_list.append(product_data)
    has_more = Product.objects.exclude(seller=user).filter(seller=seller, status='available').count() > 20
    context['init_product_data_list'] = product_data_list
    context['has_more'] = has_more
    context['error'] = error
    context['seller'] = seller
    return render(request, 'customer/shop.html', context)

def get_search_product(request, search, offset, user_id, seller_id=0):
    if request.method == 'GET':
        user = User.objects.filter(id=user_id).first()
        limit = 20 
        if seller_id==0:
            products = Product.objects.exclude(seller=user).filter(status='available', name__icontains=search)[offset:offset + limit]
            has_more = Product.objects.exclude(seller=user).filter(status='available', name__icontains=search).count() > offset + limit
        else:
            seller = User.objects.filter(id=seller_id).first()
            products = Product.objects.exclude(seller=user).filter(seller=seller, status='available', name__icontains=search)[offset:offset + limit]
            has_more = Product.objects.exclude(seller=user).filter(seller=seller, status='available', name__icontains=search).count() > offset + limit
        if 'application/json' in request.headers.get('Accept', ''):
            # Trả về JSON cho yêu cầu AJAX
            products_data = []
            for product in products:
                image = Product_Image.objects.filter(product=product).first()
                like_product = FavoriteList.objects.filter(user=user,product=product)
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'price': str(product.price),  
                    'get_sold': product.get_sold(),
                    'image_url': image.image.url if image else None,
                    'like_button_text': 'Unlike' if like_product else 'Like', 
                })
            return JsonResponse({
                'products': products_data,
                'has_more': has_more,
                'user_id':user_id,
            })

def get_more_product(request, offset, user_id, seller_id=0):
    if request.method == 'GET':
        user = User.objects.filter(id=user_id).first()
        print(offset)
        limit = 20 
        if seller_id==0:
            products = Product.objects.exclude(seller=user).filter(status='available')[offset:offset + limit]
            has_more = Product.objects.exclude(seller=user).filter(status='available').count() > offset + limit
        else:
            seller = User.objects.filter(id=seller_id).first()
            products = Product.objects.exclude(seller=user).filter(seller=seller, status='available')[offset:offset + limit]
            has_more = Product.objects.exclude(seller=user).filter(seller=seller, status='available').count() > offset + limit
        if 'application/json' in request.headers.get('Accept', ''):
            # Trả về JSON cho yêu cầu AJAX
            products_data = []
            for product in products:
                image = Product_Image.objects.filter(product=product).first()
                like_product = FavoriteList.objects.filter(user=user,product=product)
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'price': str(product.price),  
                    'get_sold': product.get_sold(),
                    'image_url': image.image.url if image else None,
                    'like_button_text': 'Unlike' if like_product else 'Like',
                })
            return JsonResponse({
                'products': products_data,
                'has_more': has_more,
                'user_id':user_id,
            })

def get_home_customer(request, user_id):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    context['user'] = user
    products = Product.objects.exclude(seller=user).filter(status='available')[:20]
    product_data_list = []
    for product in products:
        image = Product_Image.objects.filter(product=product).first()
        like = FavoriteList.objects.filter(user=user, product=product).first()
        product_data = {
            'product': product,
            'image': image,
            'like': like if like else None,
        }
        product_data_list.append(product_data)
    has_more = Product.objects.exclude(seller=user).filter(status='available').count() > 20
    context['init_product_data_list'] = product_data_list
    context['has_more'] = has_more
    context['error'] = error
    chats = Chat.objects.filter(user=user)
    context['chats']=chats
    return render(request, 'customer/home.html', context)

# ! SELLER:
def get_home_seller(request, user_id):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    context['user'] = user
    context['error'] = error
    context['month'] = timezone.now().month
    context['year'] = timezone.now().year
    return render(request,'seller/home.html',context)

def get_add_product(request, user_id):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    categories = Category.objects.all()
    context['categories'] = categories
    context['user'] = user
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = int(request.POST.get('price'))
        quantity = int(request.POST.get('quantity'))
        category_id = int(request.POST.get('category'))
        category = Category.objects.get(id=category_id)
        status = 'available'
        if quantity < 0:
            error = 'Quantity must be greater than 0'
            context['error'] = error
            return render(request,'seller/add_product.html',context)
        if quantity == 0:
            status = 'sold'
        new_product = Product.objects.create(
            seller = user,
            quantity = quantity,
            name = name,
            description = description,
            price = price,
            category = category,
            status = status,
        )
        images = request.FILES.getlist('images')
        for image in images:
            product_image = Product_Image.objects.create(product=new_product, image=image)
        script = """
            <script >
                window.close();
            </script>
        """
        return HttpResponse(script)
    return render(request,'seller/add_product.html',context)

def get_product_list(request, user_id):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    context['user'] = user
    products = Product.objects.filter(seller=user)
    product_data_list = []
    for product in products:
        img = Product_Image.objects.filter(product=product).first()
        product_data = {
            'product': product,
            'image': img
        }
        product_data_list.append(product_data)
    context['product_data_list'] = product_data_list
    return render(request,'seller/product_list.html',context)

def get_selling_history(request, user_id, month, year):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    context['user'] = user
    order_product_list = Order_Product.objects.filter(product__seller=user, order__created_at__month=month, order__created_at__year=year)
    order_product_data_list = []
    for order_product in order_product_list:
        product = order_product.product
        img = Product_Image.objects.filter(product=product).first()
        order_product_data = {
            'order_product': order_product,
            'image': img
        }
        order_product_data_list.append(order_product_data)
    context['rows'] = order_product_data_list
    previous_month = month - 1 if month > 1 else 12
    previous_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    context['previous_month'] = previous_month
    context['previous_year'] = previous_year
    if not (month == timezone.now().month and year == timezone.now().year):
        context['next_month'] = next_month
        context['next_year'] = next_year
    return render(request,'seller/selling_history.html',context)

def get_revenue(request, user_id, month, year):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    context['user'] = user
    order_product_list = Order_Product.objects.filter(product__seller=user, order__created_at__month=month, order__created_at__year=year)
    order_product_with_date = {}
    for order_product in order_product_list:
        product_date = order_product.order.created_at.date()
        if product_date not in order_product_with_date:
            order_product_with_date[product_date] = []
        order_product_with_date[product_date].append(order_product)
    
    first_day_of_month = date(year, month, 1) # Tạo đối tượng ngày đầu tháng
    _, days_in_month = calendar.monthrange(year, month) # Trả về ngày trong tuần của ngày đầu trong tháng, giá trị thứ 2 là số ngày trong tháng 
    month_dates = [first_day_of_month + timedelta(days=i) for i in range(days_in_month)] # Tạo danh sách các đối tượng ngày trong tháng
    
    weeks = []
    first_weekday = first_day_of_month.weekday()  # 0 = Thứ Hai, ..., 6 = Chủ Nhật
    first_weekday = (first_weekday + 1) % 7  # Chuyển đổi để Chủ Nhật là ngày đầu tiên của tuần
    week = [''] * first_weekday  # Thêm ngày trống cho tuần đầu tiên
    for day in month_dates:
        week.append({
            "day": day,
            "total_formatted": "{:,.0f} VND".format(sum(order_product.product.price * order_product.quantity for order_product in order_product_with_date.get(day, []))),
        })
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:  # Thêm tuần còn lại nếu chưa đủ 7 ngày
        while len(week) != 7:
            week.append({})
        weeks.append(week)
    context['weeks'] = weeks
    previous_month = month - 1 if month > 1 else 12
    previous_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    context['previous_month'] = previous_month
    context['previous_year'] = previous_year
    if not (month == timezone.now().month and year == timezone.now().year):
        context['next_month'] = next_month
        context['next_year'] = next_year
    return render(request,'seller/revenue.html',context)

def get_product_view(request, product_id):
    error = None
    context = {}
    product = Product.objects.filter(id=product_id).first()
    context['product'] = product
    images = Product_Image.objects.filter(product=product)
    context['images'] = images
    return render(request,'seller/product_view.html',context)

def get_product_edit(request, product_id):
    error = None
    context = {}
    product = Product.objects.filter(id=product_id).first()
    context['product'] = product
    images = Product_Image.objects.filter(product=product)
    context['images'] = images
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = int(request.POST.get('price'))
        quantity = int(request.POST.get('quantity'))
        category_id = int(request.POST.get('category'))
        category = Category.objects.get(id=category_id)
        status = 'available'
        if quantity < 0:
            error = 'Quantity must be greater than 0'
            context['error'] = error
            return render(request,'seller/product_edit.html',context)
        if quantity == 0:
            status = 'sold'
        product.name = name
        product.description = description
        product.price = price
        product.quantity = quantity
        product.category = category
        product.status = status
        product.save()
        images = request.FILES.getlist('images')
        if images:
            for image in images:
                product_image = Product_Image.objects.create(product=product, image=image)
        return redirect('get_product_view', product_id=product.id)
    return render(request,'seller/product_edit.html',context)

def dec_quantity(request, product_id, change):
    if request.method == 'POST':
        product = Product.objects.filter(id=product_id).first()
        new_quantity = product.quantity - change

        # Kiểm tra số lượng không âm
        if new_quantity < 0:
            return JsonResponse({
                'success': False,
                'error': 'Quantity cannot be less than 0'
            }, status=400)
        # Cập nhật status
        product.quantity = new_quantity
        if new_quantity == 0:
            product.status = 'sold'
        else:
            product.status = 'available'
        product.save()
        return JsonResponse({
            'success': True,
            'new_quantity': new_quantity,
            'new_status': product.status
        })

def inc_quantity(request, product_id, change):
    if request.method == 'POST':
        product = Product.objects.filter(id=product_id).first()
        new_quantity = product.quantity + change
        # Kiểm tra số lượng không âm
        if new_quantity < 0:
            return JsonResponse({
                'success': False,
                'error': 'Quantity cannot be less than 0'
            }, status=400)
        # Cập nhật status nếu cần
        product.quantity = new_quantity
        if new_quantity == 0:
            product.status = 'sold'
        else:
            product.status = 'available'
        product.save()
        return JsonResponse({
            'success': True,
            'new_quantity': new_quantity,
            'new_status': product.status
        })

def hide_product(request, product_id):
    if request.method == 'POST':
        product = Product.objects.filter(id=product_id).first()
        if product.status != 'hide':
            product.status = 'hide'
            product.save()
            return JsonResponse({
                'success': True,
                'new_status': product.status,
                'button_text': 'Show'
            })
        if product.quantity == 0:
            product.status = 'sold'
            product.save()
        else:
            product.status = 'available'
            product.save()
        return JsonResponse({
            'success': True,
            'new_status': product.status,
            'button_text': 'Hide'
        })

def delete_product_image(request, product_image_id):
    if request.method == 'DELETE':
        product_image = Product_Image.objects.filter(id=product_image_id).first()
        if product_image:
            product_image.delete()
            return JsonResponse({
                'success': True,
                'message': 'Image deleted successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Image not found'
            }, status=404)
# ! TEST

def get_test(request):
    return render(request,'test/test.html',context={})