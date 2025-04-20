from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.db import IntegrityError
from django.utils import timezone
from datetime import date, timedelta
import calendar
# Create your views here.

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

def get_home_customer(request, user_id):
    error = None
    context = {}
    user = User.objects.filter(id=user_id).first()
    context['user'] = user
    context['error'] = error
    return render(request,'customer/home.html',context)

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
        if images:
            print('YES')
        else:
            print('NO')
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