from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    #return HttpResponse("Rango says hey there partner! Well done Frank!")
	context_dict = {'boldmessage': "Pen, Apple, Ah, Apple-Pen!"}
	return render(request, 'rango/index.html', context = context_dict)
    
def about(request):
  #  return HttpResponse("Rango says here is the about page. <br/> <a href='/rango/about/'> About</a>")
	context_dict = {'authorname': "Frank Zhu"}
	return render(request, 'rango/about.html', context = context_dict)
