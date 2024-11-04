from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from estoreapp.models import product,Cart,Order
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail

# Create your views here.
def index(request):
    #userid=request.user.id
    #print("Logged in user is:",userid)
    #print("Request:",request.user.is_authenticated)
    context={}
    p=product.objects.filter(is_active=True)
    context['products']=p
    print(p)
    return render(request,'index.html',context)

def catfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(cat=cv)
    p=product.objects.filter(q1 & q2)
    #print(p)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def sort(request,sv):
    if sv=='0':
        col='price'
    else:
        col='-price'
    p=product.objects.filter(is_active=True).order_by(col)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def range(request):
    min=request.GET['min']
    max=request.GET['max']
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=product.objects.filter(q1 & q2 & q3)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def ulogout(request):
    logout(request)
    return redirect('/index')

def productdetails(request,pid):
    p=product.objects.filter(id=pid)
    context={}
    context['products']=p
    return render(request,'productdetails.html',context)

def addtocart(request,pid):
    if request.user.is_authenticated:
        userid=request.user.id
        #print(userid)
        #print(pid)
        u=User.objects.filter(id=userid)
        p=product.objects.filter(id=pid)
        q1=Q(uid=u[0])
        q2=Q(pid=p[0])
        c=Cart.objects.filter(q1 & q2)
        context={}
        context['products']=p
        n=len(c)
        if n==1:
            context['errmsg']="Product already exists in the cart!"
        else:
            c=Cart.objects.create(uid=u[0],pid=p[0])
            c.save()
            context['success']="Product added to the cart!"
        return render(request,'productdetails.html',context)
    else:
        return redirect('/login')
    
def viewcart(request):
    c=Cart.objects.filter(uid=request.user.id)
    s=0
    for x in c:
        s=s+x.pid.price*x.qty
    print(s)
    np=len(c)
    #print(c)
    #print(c[0].uid)
    #print(c[0].pid)
    context={}
    context['data']=c
    context['total']=s
    context['items']=np
    return render(request,'viewcart.html',context)

def remove(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')

def updateqty(request,qv,cid):
    c=Cart.objects.filter(id=cid)
    if qv=='1':
        t=c[0].qty+1
        c.update(qty=t)
    else:
        if c[0].qty>1:
            t=c[0].qty-1
            c.update(qty=t)
    return redirect('/viewcart')

def register(request):
    if request.method=="POST":
        uname=request.POST['uname']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        context={}
        if uname=="" or upass=="" or ucpass=="":
            context['errmsg']="Feilds cannot be empty!!"
            return render(request,'register.html',context)
        elif upass!=ucpass:
            context['errmsg']="Password and confirm password not matching!!"
            return render(request,'register.html',context)
        else:
            try:
                u=User.objects.create(password=upass,username=uname,email=uname)
                u.set_password(upass)
                u.save()
                context['sucmsg']="User Registered Successfully!!"
                return render(request,'register.html',context)
            except Exception:
                context['errmsg']="User with this mail id already exists!!"
                return render(request,'register.html',context)
    else:
        return render(request,'register.html')

def ulogin(request):
    if request.method=="POST":
        uname=request.POST['uname']
        upass=request.POST['upass']
        context={}
        if uname=="" or upass=="":
            context['errmsg']="Feilds cannot be empty!!"
            return render(request,'login.html',context)
        else:
            u=authenticate(username=uname,password=upass)
            #print(u)
            #print(u.username)
            # print(u.password)
            if u is not None:
                login(request,u)
                return redirect('/index')
            else:
                context['errmsg']="Invalid Uswrname/Password!!"
                return render(request,'login.html',context)
    else:
        return render(request,'login.html')
    
def placeorder(request):
    userid=request.user.id
    c=Cart.objects.filter(uid=userid)
    #print(c)
    oid=random.randrange(1000,9999)
    #print("Order is:",oid)
    for x in c:
        print(x)
        o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()
        x.delete()
    orders=Order.objects.filter(uid=userid)
    context={}
    context['data']=orders
    np=len(orders)
    s=0
    for x in orders:
        s=s+x.pid.price*x.qty
    print(s)
    context['total']=s
    context['items']=np
    return render(request,'placeorder.html',context)

def makepayment(request):
    orders=Order.objects.filter(uid=request.user.id)
    np=len(orders)
    s=0
    for x in orders:
        s=s+x.pid.price*x.qty
        oid=x.order_id
    client = razorpay.Client(auth=("rzp_test_sZ109MJm8HynPi", "QBY08QRQSxoZqH4IXVHk1oXB"))
    data = { "amount": s*100, "currency": "INR", "receipt": oid }
    payment = client.order.create(data=data)
    #print(payment)
    context={}
    context['data']=payment
    return render(request,'pay.html',context)

def sendusermail(request):
    send_mail(
    "Estore-Order Placed Successfully",
    "Order Completed!",
    "ghateyogesh004@gmail.com",
    ["ghateyogesh004@gmail.com"],
    fail_silently=False,
     )
    return render(request,'index.html')
    