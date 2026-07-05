from django.shortcuts import render, redirect
from conntoapp.models import CustomUser, UserServices
from django.db.models import Q
from django.contrib import messages
from conntoapp.choices import TeacherChoices, CustomUserChoices

# Create your views here.

def home(request):
    most_searched_services = (
        UserServices.objects.values("service_name")
        .distinct()
        .order_by("-service_search_count")[:6]
    )
    context = {
        'branches': TeacherChoices.BRANCH_CHOICES,
        'experiences': TeacherChoices.EXPERIENCE_CHOICES,
        'cities': CustomUserChoices.TURKISH_CITIES,
        'genders': CustomUserChoices.GENDER_CHOICES,
        'most_searched_services': most_searched_services,
    }
    return render(request, "home.html", context)


def searchTeacher(request):
    branch = request.GET.get("branch", "")
    experience = request.GET.get("experience", "")
    city = request.GET.get("city", "")
    gender = request.GET.get("gender", "")

    if not any([branch, experience, city, gender]):
        messages.error(request, "Lütfen en az bir filtre seçin.")
        return redirect("home")

    filters = Q()
    if branch:
        filters &= Q(branch=branch)
    if experience:
        filters &= Q(experience_years=experience)
    if city:
        filters &= Q(city=city)
    if gender:
        filters &= Q(gender=gender)

    teachers = CustomUser.objects.filter(filters).distinct()

    return render(request, "listing.html", {
        'users': teachers,
        'selected_branch': branch,
        'selected_experience': experience,
        'selected_city': city,
        'selected_gender': gender,
        'branches': TeacherChoices.BRANCH_CHOICES,
        'experiences': TeacherChoices.EXPERIENCE_CHOICES,
        'cities': CustomUserChoices.TURKISH_CITIES,
        'genders': CustomUserChoices.GENDER_CHOICES,
    })


def listing(request):
    return render(request, "listing.html", {'users': []})


def getUser(request, pk):
    user = CustomUser.objects.filter(id=pk).first()
    if user:
        user.view = user.view + 1
        user.save()
        return redirect("usersite_home", pk=user.id)
    return redirect("home")
