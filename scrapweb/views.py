from django.shortcuts import render , redirect

from django.http import HttpResponse
from scrapweb.models import *
import pymongo
import base64
import json
from bson.objectid import ObjectId
from datetime import date
# Create your views here.


Client = pymongo.MongoClient('mongodb://localhost:27017/')
db = Client['Scrap']
col_user_register = db['user_register']
col_add_product = db['add_product']
col_add_cart = db['add_cart']
col_orders = db['orders']


def index(req):
	req.session['admin']=False
	return render(req,"index.html")
def login(req):
	return render(req,"login.html")
def newauction(req):
	return render(req,"newauction.html")
def auction(req):
	return render(req,"auction.html")	
def about(req):
	return render(req,"about.html")
def contact(req):
	return render(req,"contact.html")
def sell(req):
	return render(req,"sell.html")
def signinup(req):
	return render(req,"signin-up.html")
def register(req):
	return render(req,"register.html")


'''
def home_page(request):
	list_of_items = product_list.objects.all().values()
	return render(request,"home.html",{'list_of_items':list_of_items})


	//session
	print(req.session.get('customer_id'))
	del req.session['customer_id']
	print(req.session.get('customer_id'))
	request.session['customer_id']= user['Email']
'''
def register_check(request):
	name = request.POST.get('name')
	email = request.POST.get('email')
	password = request.POST.get('password')
	cpassword = request.POST.get('cpassword')
	address = request.POST.get('address')
	number = request.POST.get('number')
	record={
		"Name":name,
		"Email":email,
		"Password" : password,
	    "Address" : address,
	    "Number" :number,
	}
	check_Email=bool(col_user_register.find_one({"Email":email}))
	if(check_Email):
		return render(request,"login.html", {'msg':'Email Already Existed'})
	else:
		if(password == cpassword):
			col_user_register.insert_one(record)
			return render(request,"login.html", {'msg':'User Registered Please Login'})
		else:
			return render(request,"register.html", {'msg':'Password is not same'})


def login_check(request):
	email = request.POST.get('email')
	password = request.POST.get('password')
	if(email == "aceecycle@mini.com" and password == "ace@123"):
		request.session['admin']=True;
		return admin_dashboard(request)
	else:
		email_check = bool(col_user_register.find_one({"Email":email}))
		if(email_check):
			user = col_user_register.find_one({"Email":email})
			if(user['Password']==password):
				request.session['customer_id']= user['Email']
				return render(request,"index.html",{'msg':user,'value':'disabled'})
			else:
				return render(request,"login.html",{'msg':'wrong credentials'})
		else:
			return render(request,"login.html",{'msg':'wrong credentials'})
 

def profile(req):
	email = req.session.get('customer_id')
	user = col_user_register.find_one({"Email":email})
	orders = list(col_orders.find({"customer_id":email}))
	for i in orders:
		i['id'] = i['_id']
		del i['_id']
	return render(req,"profile.html",{'msg':user,'orders':orders})

def profile_edit(request):
	email = request.session.get('customer_id')
	address = request.POST.get('address')
	number = request.POST.get('number')
	pin = request.POST.get('pin')
	col_user_register.update_one({"Email":email},{"$set" :{"Address":address}})
	col_user_register.update_one({"Email":email},{"$set" :{"Number":number}})
	col_user_register.update_one({"Email":email},{"$set" :{"Pin":pin}})
	user = col_user_register.find_one({"Email":email})
	return render(request,"profile.html",{'msg':user})

def add_product(request):
	user = request.session.get('customer_id')
	admin = request.session.get('admin')
	if(user or admin):
		name = request.POST.get('name')
		# image = request.FILE['image']
		image = request.POST.get('image')
		description = request.POST.get('Description')
		category = request.POST.get('category')
		quantity = request.POST.get('Quantity')
		price =  request.POST.get('price')
		record={
		"user_id":user,
		"name":name,
		"image_name":image,
		"description":description,
		"category":category,
		"quantity":quantity,
		"price":price
		}
		col_add_product.insert_one(record)
		if(admin):
			return admin_dashboard(request)
		return render(request,"sell.html",{'msg':'product saved'})
	else:
		return render(request,"login.html")

def shop(req):
	list_of_products = list(col_add_product.find())
	for i in list_of_products:
		i['id'] = i['_id']
		del i['_id']
	return render(req,"shop.html",{'list':list_of_products})

def shopsingle(req):
	r = req.get_full_path()
	id = r.split('?')
	id1=id[1]
	product = list(col_add_product.find({"_id":ObjectId(id1)}))
	return render(req,"shop-single.html",{'product':product,"id":id1})


def cart(req):
	customer_id = req.session.get('customer_id')
	if(customer_id):
		cart_products = list(col_add_cart.find({"customer_id":customer_id}))
		for i in cart_products:
			i['id'] = i['_id']
			del i['_id']
		return render(req,"cart.html",{"list":cart_products})
	return render(req, "login.html")

def add_cart(req):
	customer_id = req.session.get('customer_id')
	product_id = req.POST.get('product_id')
	quantity =  req.POST.get('product-quanity') 
	product = list(col_add_product.find({"_id":ObjectId(product_id)}))
	price = product[0]['price']
	name = product[0]['name']
	total = int(price) * int(quantity)
	record={
	"customer_id":customer_id,
	"product_name":name,
	"price":price,
	"quantity":quantity,
	"total":total
	}
	col_add_cart.insert_one(record)
	cart_products = list(col_add_cart.find({"customer_id":customer_id}))
	return render(req,"cart.html",{"list":cart_products})

def remove_cart(req):
	customer_id = req.session.get('customer_id')
	r = req.get_full_path()
	id = r.split('?')
	id1=id[1]
	col_add_cart.delete_one({"_id":ObjectId(id1),"customer_id":customer_id})
	return redirect(cart)

def payment(req):
	customer_id = req.session.get('customer_id')
	cart_products = list(col_add_cart.find({"customer_id":customer_id}))
	for j in cart_products:
		col_orders.insert_one(j)
	for i in cart_products:
		col_add_cart.delete_one(i)
	return profile(req)

def admin_dashboard(req):
	products = list(col_add_product.find())
	for i in products:
		i['id'] = i['_id']
		del i['_id']
	productsLen = len(products)
	users = list(col_user_register.find())
	userslen = len(users)
	orders = list(col_orders.find())
	ordersLen = len(orders)
	return render(req,"admina.html",{"productsLen":productsLen,"userslen":userslen,"ordersLen":ordersLen,"orders":orders ,"products":products})

def remove_product(req):
	r = req.get_full_path()
	id = r.split('?')
	id1=id[1]
	col_add_product.delete_one({"_id":ObjectId(id1)})
	return admin_dashboard(req)
