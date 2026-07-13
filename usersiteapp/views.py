from django.shortcuts import render, get_object_or_404, redirect
from conntoapp.models import CustomUser, UserWorks
from conntoapp.course_center_auth import redirect_if_cannot_view_usersite

# Create your views here.

def _require_usersite_access(request, pk):
    return redirect_if_cannot_view_usersite(request, pk)


def index(request, pk):
    redirect_response = _require_usersite_access(request, pk)
    if redirect_response:
        return redirect_response
    user = getUser(pk)
    return render(request, "index.html", {'user':user})

def about(request, pk):
    redirect_response = _require_usersite_access(request, pk)
    if redirect_response:
        return redirect_response
    user = getUser(pk)
    return render(request, "about.html", {'user':user})


def contact(request, pk):
    redirect_response = _require_usersite_access(request, pk)
    if redirect_response:
        return redirect_response
    user = getUser(pk)
    return render(request, "contact.html", {'user':user})

def credentials(request, pk):
    redirect_response = _require_usersite_access(request, pk)
    if redirect_response:
        return redirect_response
    user = getUser(pk)
    return render(request, "credentials.html", {'user':user})

def services(request, pk):
    redirect_response = _require_usersite_access(request, pk)
    if redirect_response:
        return redirect_response
    user = getUser(pk)
    return render(request, "services.html", {'user':user})

def work(request, pk):
    redirect_response = _require_usersite_access(request, pk)
    if redirect_response:
        return redirect_response
    user = getUser(pk)
    return render(request, "works.html", {'user':user})

def workDetails(request, pk, workId):
    redirect_response = _require_usersite_access(request, pk)
    if redirect_response:
        return redirect_response
    user = getUser(pk)
    work = get_object_or_404(UserWorks, id=workId, custom_user=user)
    return render(request, "work-detail.html", {'user': user, 'work': work})


def getUser(pk):
    user = CustomUser.objects.filter(id = pk).first()
    return user

