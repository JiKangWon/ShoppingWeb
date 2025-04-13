from django.shortcuts import render
from .models import *
from django.db import IntegrityError
# Create your views here.
# ! CUSTOMER
def get_register_customer(request):
    error = None
    if request.method=='POST':
        post_username = request.POST.get('username')
        post_password = request.POST.get('password')
        post_password_confirm = request.POST.get('password_confirm')
        post_name = request.POST.get('name')
        if post_password != post_password_confirm:
            error = 'Password does not match'
        else:
            try:
                User.objects.create(
                    username = post_username,
                    password = post_password,
                    name = post_name,
                    balance = 0,
                    role = 'customer',
                )
                return get_login_customer(request)
            except IntegrityError:
                error = 'Username already exists'
    context = {
        'error': error,
    }
    return render(request, 'customer/register.html', context=context)

def get_login_customer(request):
    error = None
    if request.method=='POST':
        post_username = request.POST.get('username')
        post_password = request.POST.get('password')
        try:
            user = User.objects.get(username=post_username, password=post_password, role='customer')
            return render(request, 'customer/home.html', context={'user': user})
        except User.DoesNotExist:
            error = 'Invalid username or password'
    context = {
        'error': error,
    }
    return render(request, 'customer/login.html', context=context)
# ! SELLER
def get_register_seller(request):
    error = None
    if request.method=='POST':
        post_username = request.POST.get('username')
        post_password = request.POST.get('password')
        post_password_confirm = request.POST.get('password_confirm')
        post_name = request.POST.get('name')
        if post_password != post_password_confirm:
            error = 'Password does not match'
        else:
            try:
                User.objects.create(
                    username = post_username,
                    password = post_password,
                    name = post_name,
                    balance = 0,
                    role = 'seller',
                )
                return get_login_seller(request)
            except IntegrityError:
                error = 'Username already exists'
    context = {
        'error': error,
    }
    return render(request, 'seller/register.html', context=context)

def get_login_seller(request):
    error = None
    if request.method=='POST':
        post_username = request.POST.get('username')
        post_password = request.POST.get('password')
        try:
            user = User.objects.get(username=post_username, password=post_password, role='seller')
            return render(request, 'seller/home.html', context={'user': user})
        except User.DoesNotExist:
            error = 'Invalid username or password'
    context = {
        'error': error,
    }
    return render(request, 'seller/login.html', context=context)
# ! TEST
def get_test(request):
    return render(request,'test/test.html',context={})