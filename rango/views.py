from django.shortcuts import render, redirect

from rango.models import Category

from rango.models import Page

from rango.forms import CategoryForm

from rango.forms import PageForm

from rango.forms import UserForm, UserProfileForm

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse

from django.contrib.auth.decorators import login_required

from datetime import datetime

from django.contrib.auth.models import User

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
	context_dict = {'form': form}

	return render(request, 'rango/add_category.html', context_dict)
			
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

def get_category_list(max_results=0, starts_with=''):
	cat_list = []

	if starts_with:
		cat_list = Category.objects.filter(name__startswith=starts_with)
	else:
		cat_list = Category.objects.all()
	
	if max_results > 0:
		if len(cat_list) > max_results:
			cat_list = cat_list[:max_results]

	return cat_list

def suggest_category(request):
	cat_list = []
	starts_with = ''
	if request.method == 'GET':
		starts_with = request.GET['suggestion']
		cat_list = get_category_list(8, starts_with)
	context_dict = {'cat_list': cat_list}
	return render(request, 'rango/category_list.html', context_dict)
	
@login_required
def profile(request):
	u = User.objects.get(username = request.user)

	try:
		up = Userprofile.objects.get(user = u)
	except:
		up = None

	context_dict["user"] = u
	context_dict["userprofile"] = up

	return render(request, 'rango/profile.html', context_dict)


def track_url(request):
	page_id = None
	url = '/rango/'
	if request.method == "GET":
		if 'page_id' in request.GET:
			page_id = request.GET["page_id"]
			try:
				page = Page.objects.get(id=page_id)
				page.views = page.views + 1
				page.save()
				url = page.url

			except:
				pass

	return redirect(url)

@login_required
def like_category(request):
	cat_id = None
	if request.method == 'GET':
		cat_id = request.GET['category_id']

	likes = 0
	if cat_id:
		category = Category.objects.get(id=int(cat_id))
		if category:
			likes = category.likes + 1
			category.likes = likes
			category.save()

	return HttpResponse(likes)
