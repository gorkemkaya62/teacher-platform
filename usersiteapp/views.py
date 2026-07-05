from django.shortcuts import render, get_object_or_404, redirect
from conntoapp.models import CustomUser, UserWorks, UserBlogs
from django.urls import reverse

# Create your views here.

def index(request, pk):
    user = getUser(pk)
    return render(request, "index.html", {'user':user})

def about(request, pk):
    user = getUser(pk)
    return render(request, "about.html", {'user':user})


def contact(request, pk):
    user = getUser(pk)
    return render(request, "contact.html", {'user':user})

def credentials(request, pk):
    user = getUser(pk)
    return render(request, "credentials.html", {'user':user})

def services(request, pk):
    user = getUser(pk)
    return render(request, "services.html", {'user':user})

def work(request, pk):
    user = getUser(pk)
    return render(request, "works.html", {'user':user})

def workDetails(request, pk, workName):
    user = getUser(pk)
    work = UserWorks.objects.filter(work_name = workName).first()
    return render(request, "work-detail.html", {'user':user, 'work':work})

def blog(request, pk):
    user = getUser(pk)
    mostViewBlogs = user.userblogs.all().order_by('-blog_view')[:5]
    return render(request, "blog.html", {'user':user, 'mostViewBlogs':mostViewBlogs})

def blogDetails(request, pk, blogId):
    user = getUser(pk)
    blog = UserBlogs.objects.filter(id = blogId).first()
    blog.blog_view = blog.blog_view + 1
    blog.save()
    mostViewBlogs = user.userblogs.all().order_by('-blog_view')[:5]

    return render(request, "blog-detail.html", {'user':user ,'blog':blog, 'mostViewBlogs':mostViewBlogs})


def getUser(pk):
    user = CustomUser.objects.filter(id = pk).first()
    return user

    
