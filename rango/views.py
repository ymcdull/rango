from django.shortcuts import render

from django.http import HttpResponse

from rango.models import Category

from rango.models import Page

from rango.forms import CategoryForm

from rango.forms import PageForm

def index(request):
    #return HttpResponse("Rango says hey there partner! Well done Frank!")
	category_list = Category.objects.order_by('-likes')[:5]
	pages_list = Page.objects.order_by('-views')[:5]
#	context_dict = {'boldmessage': "Pen, Apple, Ah, Apple-Pen!"}
	context_dict = {'categories' : category_list, 'pages' : pages_list}
	return render(request, 'rango/index.html', context = context_dict)
    
def about(request):
  #  return HttpResponse("Rango says here is the about page. <br/> <a href='/rango/about/'> About</a>")
	context_dict = {'authorname': "Frank Zhu"}
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


