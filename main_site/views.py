from django.shortcuts import render

# Create your views here.
# ! CUSTOMER
def get_register_customer(request):
    context = {}
    if request.method=='POST':
        pass
    return render(request, 'customer/register.html', context=context)
# ! SELLER

# ! TEST
def get_test(request):
    return render(request,'test/test.html',context={})