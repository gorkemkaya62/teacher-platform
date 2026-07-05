from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import (
    TeacherRegisterForm, TeacherLoginForm, TeacherProfileForm, TeacherSkillForm,
    TeacherEducationForm, TeacherExperienceForm, TeacherServiceForm, TeacherWorkForm,
    PasswordChangeForm, TeacherBlogForm, TeacherCertificateForm,
    CourseCenterRegisterForm, AdminLoginForm,
)
from .models import (
    CustomUser, UserSkill, UserEducation, UserExperience, UserServices,
    UserWorks, UserBlogs, UserAwards, CourseCenter, AdminUser,
)
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from datetime import date
import string
import random
from django.core.mail import send_mail
from .district_data import get_district_choices



# Create your views here.

def adminlogin(request):
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect("addItems")
    if 'course_center_id' in request.session:
        return redirect("/home/")

    if request.method == "POST":
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            is_course_center = form.cleaned_data["is_course_center"]

            if is_course_center:
                try:
                    course_center = CourseCenter.objects.get(email=email)
                    if course_center.check_password(password):
                        request.session['course_center_id'] = course_center.id
                        request.session['is_course_center'] = True
                        messages.success(request, "Kurs merkezi olarak başarıyla giriş yapıldı")
                        return redirect("/home/")
                    else:
                        messages.error(request, "Kurs merkezi hesabı için geçersiz şifre")
                except CourseCenter.DoesNotExist:
                    messages.error(request, "Bu e-posta ile kayıtlı kurs merkezi bulunamadı")
            else:
                try:
                    user = CustomUser.objects.get(email=email)
                    if user.check_password(password):
                        login(request, user)
                        messages.success(request, "Başarıyla giriş yapıldı")
                        return redirect("addItems")
                    else:
                        messages.error(request, "Öğretmen hesabı için geçersiz şifre")
                except CustomUser.DoesNotExist:
                    messages.error(request, "Bu e-posta ile kayıtlı öğretmen bulunamadı")
            
            return redirect("login")
    else:
        form = TeacherLoginForm()
    
    return render(request, "admintemplate/login.html", {'form': form})

def adminregister(request):
    if request.user.is_authenticated: 
        return redirect("addItems")
    
    if request.method == "POST":
        is_course_center = request.POST.get('is_course_center', False)

        if is_course_center:
            course_center_form = CourseCenterRegisterForm(request.POST)

            if course_center_form.is_valid():
                try:
                    course_center_form.save()
                    messages.success(request, "Kurs merkezi kaydı başarılı. Giriş yapabilirsiniz")
                    return redirect("login")
                except Exception as e:
                    messages.error(request, str(e))
                    return redirect("register")
            else:
                for field, errors in course_center_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{error}")
                return redirect("register")
        else:
            user_form = TeacherRegisterForm(request.POST)
            if user_form.is_valid():
                try:
                    user = user_form.save(commit=False)
                    user.set_password(user_form.cleaned_data["password"])
                    user.username = user_form.cleaned_data["email"]
                    user.save()
                    messages.success(request, "Öğretmen kaydı başarılı. Giriş yapabilirsiniz")
                    return redirect("login")
                except Exception as e:
                    messages.error(request, str(e))
                    return redirect("register")
            else:
                for field, errors in user_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{error}")
                return redirect("register")
    else:
        user_form = TeacherRegisterForm()
        course_center_form = CourseCenterRegisterForm()

    return render(request, "admintemplate/register.html", {
        'form': user_form,
        'course_center_form': course_center_form,
    })


def district_choices_api(request):
    city = request.GET.get("city", "")
    districts = [
        {"value": value, "label": label}
        for value, label in get_district_choices(city)
        if value
    ]
    return JsonResponse({"districts": districts})


def adminlogout(request):
    if 'course_center_id' in request.session:
        del request.session['course_center_id']
        del request.session['is_course_center']
        messages.success(request, "Kurs merkezi hesabından çıkış yapıldı")
    else:
        logout(request)
        messages.success(request, "Successfully logged out")
    return redirect("login")

# FORGOT PASSWORD
    
def forgotPassword(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = CustomUser.objects.filter(email=email).first()
        if user is not None:
            newPassword = generate_random_password()
            user.set_password(newPassword)
            user.save()
            
            send_mail(
                "Forgot Password",
                f"Hello {user.fullname},\n\nNew Password: {newPassword}\nPlease change your password when you are login.",
                "forgotpassword@ogretmenim.com",
                [user.email],
                fail_silently=False
            )
            messages.success(request, "Your new password has been send to your email")
            return redirect("forgotPassword")
        else:
            messages.error(request, "There is no account")
            return redirect("forgotPassword")
        
    return render(request, "admintemplate/forgot-password.html")

def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# FORGOT PASSWORD




# Add Item Part Start


@login_required
def addItems(request):
    context = {
        'teacherProfileForm': TeacherProfileForm(instance=request.user),
        'teacherSkillForm': TeacherSkillForm(),
        'teacherEducationForm': TeacherEducationForm(),
        'teacherExperienceForm': TeacherExperienceForm(),
        'teacherServiceForm': TeacherServiceForm(),
        'teacherWorkForm': TeacherWorkForm(),
        'teacherBlogForm': TeacherBlogForm(),
        'teacherCertificateForm': TeacherCertificateForm(),
    }
    return render(request, "admintemplate/add-items.html", context)


@login_required
def teacherProfileAccept(request):
    if request.method == "POST":
        form = TeacherProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("addItems")
        else:
            print(form.errors)
    else:
        return redirect("addItems")

@login_required
def teacherSkillAccept(request):
    if request.method == "POST":
        form = TeacherSkillForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["skill_degree"] > 100 or form.cleaned_data["skill_degree"] < 0:
                messages.error(request, "Yetkinlik seviyesi 0-100 arasında olmalıdır")
                return redirect("addItems")
            skill = form.save(commit=False)
            skill.custom_user = request.user
            skill.save()
            return redirect("addItems")
    else:
        return redirect("addItems")

@login_required
def teacherEducationAccept(request):
    if request.method == "POST":
        form = TeacherEducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.custom_user = request.user
            education.save()
            return redirect("addItems")
    else:
        return redirect("addItems")
    
@login_required
def teacherCertificateAccept(request):
    if request.method == "POST":
        form = TeacherCertificateForm(request.POST)
        if form.is_valid():
            award = form.save(commit=False)
            award.custom_user = request.user
            award.save()
            return redirect("addItems")
    else:
        return redirect("addItems")

@login_required
def teacherExperienceAccept(request):
    if request.method == "POST":
        form = TeacherExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.custom_user = request.user
            experience.save()
            return redirect("addItems")
    else:
        return redirect("addItems")
    
@login_required
def teacherServiceAccept(request):
    if request.method == "POST":
        form = TeacherServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.custom_user = request.user
            service.save()
            return redirect("addItems")
    else:
        return redirect("addItems")

@login_required
def teacherWorkAccept(request):
    if request.method == "POST":
        form = TeacherWorkForm(request.POST, request.FILES)
        if form.is_valid():
            work = form.save(commit=False)
            work.custom_user = request.user
            work.save()
            return redirect("addItems")
    else:
        return redirect("addItems")
    
@login_required
def teacherBlogAccept(request):
    if request.method == "POST":
        form = TeacherBlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.custom_user = request.user
            blog.blog_date = date.today()
            blog.save()
            return redirect("addItems")
    else:
        return redirect("addItems")
    
    
# Listing Area start
@login_required
def listingSkill(request):
    return render(request, "admintemplate/listing-skill.html")

@login_required
def listingEducation(request):
    return render(request, "admintemplate/listing-education.html")

@login_required
def listingExperience(request):
    return render(request, "admintemplate/listing-experience.html")

@login_required
def listingService(request):
    return render(request, "admintemplate/listing-service.html")

@login_required
def listingWork(request):
    return render(request, "admintemplate/listing-work.html")

@login_required
def listingBlog(request):
    return render(request, "admintemplate/listing-blog.html")

@login_required
def listingAward(request):
    return render(request, "admintemplate/listing-award.html")

# Listing Area End

# Update Area Start
@login_required
def updatePassword(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            form.save()
            messages.success(request, "Success")
            login(request, user)
            return redirect("updatePassword")
        else:
            messages.error(request, "Please check your informations")
            return redirect("updatePassword")
    else:
        form = PasswordChangeForm(request.user)
        return render(request, "admintemplate/update.html", {'form':form})

@login_required
def updateSkill(request, pk):
    skill = UserSkill.objects.filter(id = pk).first()
    if request.method == "POST":
        form = TeacherSkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            return redirect("listingSkill")
    else:
        form = TeacherSkillForm(instance=skill)
        return render(request, "admintemplate/update.html", {'form': form})

@login_required
def updateEducation(request, pk):
    education = UserEducation.objects.filter(id = pk).first()
    if request.method == "POST":
        form = TeacherEducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            return redirect("listingEducation")
    else:
        form = TeacherEducationForm(instance=education)
        return render(request, "admintemplate/update.html", {'form': form})
    
@login_required
def updateExperience(request, pk):
    experience = UserExperience.objects.filter(id = pk).first()
    if request.method == "POST":
        form = TeacherExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            return redirect("listingExperience")
    else:
        form = TeacherExperienceForm(instance=experience)
        return render(request, "admintemplate/update.html", {'form': form})
    
@login_required
def updateAward(request, pk):
    award = UserAwards.objects.filter(id = pk).first()
    if request.method == "POST":
        form = TeacherCertificateForm(request.POST, instance=award)
        if form.is_valid():
            form.save()
            return redirect("listingAward")
    else:
        form = TeacherCertificateForm(instance=award)
        return render(request, "admintemplate/update.html", {'form':form})
    
@login_required
def updateService(request, pk):
    service = UserServices.objects.filter(id = pk).first()
    if request.method == "POST":
        form = TeacherServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect("listingService")
    else:
        form = TeacherServiceForm(instance=service)
        return render(request, "admintemplate/update.html", {'form': form})
    
@login_required
def updateWork(request, pk):
    work = UserWorks.objects.filter(id = pk).first()
    if request.method == "POST":
        form = TeacherWorkForm(request.POST, request.FILES, instance=work)
        if form.is_valid():
            form.save()
            return redirect("listingWork")
    else:
        form = TeacherWorkForm(instance=work)
        return render(request, "admintemplate/update.html", {'form': form})
    
@login_required
def updateBlog(request, pk):
    blog = UserBlogs.objects.filter(id = pk).first()
    if request.method == "POST":
        form = TeacherBlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect("listingBlog")
    else:
        form = TeacherBlogForm(instance=blog)
        return render(request, "admintemplate/update.html", {'form':form})
    
# Update Area End

# Delete Area Start

@login_required
def deleteSkill(request, pk):
    skill = UserSkill.objects.filter(id=pk).first()
    skill.delete()
    return redirect("listingSkill")

@login_required
def deleteEducation(request, pk):
    education = UserEducation.objects.filter(id=pk).first()
    education.delete()
    return redirect("listingEducation")

@login_required
def deleteExperience(request, pk):
    experience = UserExperience.objects.filter(id=pk).first()
    experience.delete()
    return redirect("listingExperience")

@login_required
def deleteService(request, pk):
    service = UserServices.objects.filter(id=pk).first()
    service.delete()
    return redirect("listingService")

@login_required
def deleteWork(request, pk):
    work = UserWorks.objects.filter(id=pk).first()
    work.delete()
    return redirect("listingWork")

@login_required
def deleteBlog(request, pk):
    blog = UserBlogs.objects.filter(id = pk).first()
    blog.delete()
    return redirect("listingBlog")

@login_required
def deleteAward(request, pk):
    award = UserAwards.objects.filter(id = pk).first()
    award.delete()
    return redirect("listingAward")

# LOGOUT

@login_required
def loginout(request):
    logout(request)
    messages.success(request, "Başarıyla çıkış yapıldı")
    return redirect("login")

def admin_panel_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                admin_user = AdminUser.objects.get(username=username)
                if admin_user.check_password(password):
                    request.session['admin_id'] = admin_user.id
                    messages.success(request, 'Login successful!')
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Invalid password!')
            except AdminUser.DoesNotExist:
                messages.error(request, 'User not found!')
    else:
        form = AdminLoginForm()
    
    return render(request, 'admintemplate/admin-login.html', {'form': form})

def admin_logout(request):
    if 'admin_id' in request.session:
        del request.session['admin_id']
        messages.success(request, "Logout successful")
    return redirect('admin_panel_login')

def admin_dashboard(request):
    if 'admin_id' not in request.session:
        return redirect('admin_panel_login')
        
    users = CustomUser.objects.all()
    course_centers = CourseCenter.objects.all()

    context = {
        'users': users,
        'course_centers': course_centers,
        'total_users': users.count(),
        'total_course_centers': course_centers.count(),
    }
    
    return render(request, "admintemplate/admin-dashboard.html", context)

def admin_user_detail(request, user_id):
    if 'admin_id' not in request.session:
        return redirect('admin_panel_login')
        
    user = get_object_or_404(CustomUser, id=user_id)
    skills = UserSkill.objects.filter(custom_user=user)
    educations = UserEducation.objects.filter(custom_user=user)
    experiences = UserExperience.objects.filter(custom_user=user)
    services = UserServices.objects.filter(custom_user=user)
    works = UserWorks.objects.filter(custom_user=user)
    blogs = UserBlogs.objects.filter(custom_user=user)
    awards = UserAwards.objects.filter(custom_user=user)
    
    context = {
        'user': user,
        'skills': skills,
        'educations': educations,
        'experiences': experiences,
        'services': services,
        'works': works,
        'blogs': blogs,
        'awards': awards
    }
    
    return render(request, "admintemplate/admin-user-detail.html", context)

def admin_course_center_detail(request, course_center_id):
    if 'admin_id' not in request.session:
        return redirect('admin_panel_login')

    course_center = get_object_or_404(CourseCenter, id=course_center_id)

    context = {
        'course_center': course_center,
    }

    return render(request, "admintemplate/admin-course-center-detail.html", context)

def admin_delete_user(request, user_id):
    if 'admin_id' not in request.session:
        return redirect('admin_panel_login')
        
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.success(request, "Öğretmen başarıyla silindi")
    return redirect('admin_dashboard')

def admin_delete_course_center(request, course_center_id):
    if 'admin_id' not in request.session:
        return redirect('admin_panel_login')

    course_center = get_object_or_404(CourseCenter, id=course_center_id)
    course_center.delete()
    messages.success(request, "Kurs merkezi başarıyla silindi")
    return redirect('admin_dashboard')