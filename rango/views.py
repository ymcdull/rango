from django.shortcuts import render

from rango.models import Category

from rango.models import Page

from rango.forms import CategoryForm

from rango.forms import PageForm

from rango.forms import UserForm, UserProfileForm

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse

from django.contrib.auth.decorators import login_required

from datetime import datetime

def index(request):
    #return HttpResponse("Rango says hey there partner! Well done Frank!")
	category_list = Category.objects.order_by('-likes')[:5]
	pages_list = Page.objects.order_by('-views')[:5]
#	context_dict = {'boldmessage': "Pen, Apple, Ah, Apple-Pen!"}
	context_dict = {'categories' : category_list, 'pages' : pages_list}
	#return render(request, 'rango/index.html', context = context_dict)
	#response = render(request, 'rango/index.html', context = context_dict)
	#visits = int(request.COOKIES.get('visits', '0'))
	
	if request.session.get('last_visit'):
		last_visit_time = request.session.get('last_visit')
		visits = request.session.get('visits', 0)
		last_visit_time = datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")

		if (datetime.now() - last_visit_time).days > 0:
			request.session['visits'] = visits + 1
			request.session['last_visit'] = str(datetime.now())
	else:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = 1

	return render(request, 'rango/index.html', context_dict)
		

def about(request):
  #  return HttpResponse("Rango says here is the about page. <br/> <a href='/rango/about/'> About</a>")
	if request.session.get('visits'):
		count = request.session.get('visits')
	else:
		count = 0	
	context_dict = {'authorname': "Frank Zhu", 'visits': count}
	return render(request, 'rango/about.html', context = context_dict)


def show_category(request, category_name_slug):
	context_dict = {}

	try:
		category = Category.objects.get(slug= category_name_slug)
		pages = Page.objects.filter(category = category)

		context_dict['category'] = category
		context_dict['pages'] = pages


	except Category.DoesNotExist:
		context_dict['category'] = None
		context_dict['pages'] = None

	return render(request, 'rango/category.html', context = context_dict)

@login_required
def add_category(request):
	form = CategoryForm()

	if request.method == 'POST':
		form = CategoryForm(request.POST)
		if form.is_valid():
			cat = form.save(commit=True)
			print(cat, cat.slug)
			return index(request)

		else:
			print(form.errors)

	return render(request, 'rango/add_category.html', {'form': form})
			
@login_required
def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None

	form = PageForm()
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
				return show_category(request, category_name_slug)
			else:
				print(form.errors)
	context_dict = {'form': form, 'category': category}
	return render(request, 'rango/add_page.html', context_dict)

def register(request):
	registered = False

	if request.method == 'POST':
		user_form = UserForm(data = request.POST)
		profile_form = UserProfileForm(data = request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()

			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picutre']
			profile.save()
			registered = True

		else:
			print user_form.errors, profile_form.errors
	
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	context_dict = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered}

	return render(request, 'rango/register.html', context_dict) 
				

def user_login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(username = username, password = password)

		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/rango/')

			else:
				#return HttpResponse("Your Rango account is disabled")
				return render(request, 'rango/login.html', {"disabled_account": True})

		else:
			print("Invalid login details: {0}, {1}".format(username, password))
			#return HttpResponse("Invalid login details supplied.")
			return render(request, 'rango/login.html', {"bad_details": True})

	else:
		return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
	#return HttpResponse("Since you're logged in, you can see this text!")
	return render(request, 'rango/restricted.html', {})

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/rango/')








