from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from .forms import (
    TeacherRegisterForm, TeacherLoginForm, TeacherProfileForm, TeacherSkillForm,
    TeacherEducationForm, TeacherExperienceForm, TeacherServiceForm, TeacherWorkForm,
    TeacherPasswordChangeForm, TeacherCertificateForm,
    CourseCenterRegisterForm, AdminLoginForm,
)
from .models import (
    CustomUser, UserSkill, UserEducation, UserExperience, UserServices,
    UserWorks, UserAwards, CourseCenter, AdminUser,
)
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import date
import string
import random
from django.core.mail import send_mail
from .district_data import get_district_choices
from .user_presence import get_active_user_snapshot



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
        if not request.POST.get('checkBox'):
            messages.error(request, "Kayıt olmak için kullanım şartlarını kabul etmelisiniz.")
            return redirect("register")

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
        course_center_id = request.session.get('course_center_id')
        if course_center_id:
            CourseCenter.objects.filter(pk=course_center_id).update(last_seen=None)
        del request.session['course_center_id']
        del request.session['is_course_center']
        messages.success(request, "Kurs merkezi hesabından çıkış yapıldı")
    else:
        if request.user.is_authenticated:
            CustomUser.objects.filter(pk=request.user.pk).update(last_seen=None)
        logout(request)
        messages.success(request, "Başarıyla çıkış yapıldı")
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
                "Şifremi Unuttum",
                f"Merhaba {user.fullname},\n\nYeni Şifreniz: {newPassword}\nLütfen giriş yaptıktan sonra şifrenizi değiştirin.",
                "forgotpassword@ogretmenim.com",
                [user.email],
                fail_silently=False
            )
            messages.success(request, "Yeni şifreniz e-posta adresinize gönderildi")
            return redirect("forgotPassword")
        else:
            messages.error(request, "Bu e-posta ile kayıtlı hesap bulunamadı")
            return redirect("forgotPassword")
        
    return render(request, "admintemplate/forgot-password.html")

def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# FORGOT PASSWORD




# Add Item Part Start

ADD_ITEMS_TAB_ALIASES = {
    'profile': 'profile',
    'skills': 'skills',
    'educations': 'educations',
    'experiences': 'experiences',
    'services': 'services',
    'certificates': 'certificates',
    'works': 'works',
}


def _redirect_add_items_tab(tab='profile'):
    tab = ADD_ITEMS_TAB_ALIASES.get(tab, tab)
    return redirect(f"{reverse('addItems')}?tab={tab}")


def _add_items_context(user, active_tab=None, **form_overrides):
    context = {
        'teacherProfileForm': TeacherProfileForm(instance=user),
        'teacherSkillForm': TeacherSkillForm(),
        'teacherEducationForm': TeacherEducationForm(),
        'teacherExperienceForm': TeacherExperienceForm(),
        'teacherServiceForm': TeacherServiceForm(),
        'teacherWorkForm': TeacherWorkForm(),
        'teacherCertificateForm': TeacherCertificateForm(),
    }
    context.update(form_overrides)
    if active_tab:
        context['active_tab'] = active_tab
    return context


def _add_items_tab_from_post(request, default='profile'):
    tab = request.POST.get('active_tab', default)
    return ADD_ITEMS_TAB_ALIASES.get(tab, default)


def _is_add_items_post(request):
    return request.POST.get('form_source') == 'add_items'


@login_required
def addItems(request):
    active_tab = request.GET.get('tab')
    return render(request, "admintemplate/add-items.html", _add_items_context(
        request.user,
        active_tab=active_tab,
    ))


@login_required
def teacherProfileAccept(request):
    if request.method != "POST":
        return _redirect_add_items_tab('profile')

    tab = _add_items_tab_from_post(request, 'profile')
    form = TeacherProfileForm(request.POST, request.FILES, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Profil bilgileri kaydedildi.")
        return _redirect_add_items_tab(tab)

    return render(
        request,
        "admintemplate/add-items.html",
        _add_items_context(request.user, active_tab=tab, teacherProfileForm=form),
    )

@login_required
def teacherSkillAccept(request):
    if request.method == "POST":
        from_add_items = _is_add_items_post(request)
        tab = _add_items_tab_from_post(request, 'skills')
        form = TeacherSkillForm(request.POST, user=request.user)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.custom_user = request.user
            skill.save()
            messages.success(request, "Yetkinlik kaydedildi.")
            if from_add_items:
                return _redirect_add_items_tab(tab)
            return redirect("listingSkill")

        if from_add_items:
            return render(
                request,
                "admintemplate/add-items.html",
                _add_items_context(request.user, active_tab=tab, teacherSkillForm=form),
            )

        return render(request, "admintemplate/listing-skill.html", {
            'teacherSkillForm': form,
        })

    return redirect("listingSkill")

@login_required
def teacherEducationAccept(request):
    if request.method != "POST":
        return _redirect_add_items_tab('educations')

    tab = _add_items_tab_from_post(request, 'educations')
    form = TeacherEducationForm(request.POST)
    if form.is_valid():
        education = form.save(commit=False)
        education.custom_user = request.user
        education.save()
        messages.success(request, "Eğitim bilgisi kaydedildi.")
        return _redirect_add_items_tab(tab)

    return render(
        request,
        "admintemplate/add-items.html",
        _add_items_context(request.user, active_tab=tab, teacherEducationForm=form),
    )
    
@login_required
def teacherCertificateAccept(request):
    if request.method != "POST":
        return _redirect_add_items_tab('certificates')

    tab = _add_items_tab_from_post(request, 'certificates')
    form = TeacherCertificateForm(request.POST)
    if form.is_valid():
        award = form.save(commit=False)
        award.custom_user = request.user
        award.save()
        messages.success(request, "Sertifika kaydedildi.")
        return _redirect_add_items_tab(tab)

    return render(
        request,
        "admintemplate/add-items.html",
        _add_items_context(request.user, active_tab=tab, teacherCertificateForm=form),
    )

@login_required
def teacherExperienceAccept(request):
    if request.method != "POST":
        return _redirect_add_items_tab('experiences')

    tab = _add_items_tab_from_post(request, 'experiences')
    form = TeacherExperienceForm(request.POST)
    if form.is_valid():
        experience = form.save(commit=False)
        experience.custom_user = request.user
        experience.save()
        messages.success(request, "Deneyim kaydedildi.")
        return _redirect_add_items_tab(tab)

    return render(
        request,
        "admintemplate/add-items.html",
        _add_items_context(request.user, active_tab=tab, teacherExperienceForm=form),
    )
    
@login_required
def teacherServiceAccept(request):
    if request.method != "POST":
        return _redirect_add_items_tab('services')

    tab = _add_items_tab_from_post(request, 'services')
    form = TeacherServiceForm(request.POST)
    if form.is_valid():
        service = form.save(commit=False)
        service.custom_user = request.user
        service.save()
        messages.success(request, "Ders bilgisi kaydedildi.")
        return _redirect_add_items_tab(tab)

    return render(
        request,
        "admintemplate/add-items.html",
        _add_items_context(request.user, active_tab=tab, teacherServiceForm=form),
    )

@login_required
def teacherWorkAccept(request):
    if request.method != "POST":
        return _redirect_add_items_tab('works')

    tab = _add_items_tab_from_post(request, 'works')
    form = TeacherWorkForm(request.POST)
    if form.is_valid():
        work = form.save(commit=False)
        work.custom_user = request.user
        work.save()
        messages.success(request, "Ders materyali kaydedildi.")
        return _redirect_add_items_tab(tab)

    return render(
        request,
        "admintemplate/add-items.html",
        _add_items_context(request.user, active_tab=tab, teacherWorkForm=form),
    )
    
# Listing Area start
@login_required
def listingSkill(request):
    return render(request, "admintemplate/listing-skill.html", {
        'teacherSkillForm': TeacherSkillForm(),
    })

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
def listingAward(request):
    return render(request, "admintemplate/listing-award.html")

# Listing Area End

# Update Area Start
@login_required
def updatePassword(request):
    if request.method == "POST":
        form = TeacherPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            form.save()
            messages.success(request, "Şifreniz başarıyla güncellendi")
            login(request, user)
            return redirect("updatePassword")
        else:
            messages.error(request, "Lütfen bilgilerinizi kontrol edin")
            return redirect("updatePassword")
    else:
        form = TeacherPasswordChangeForm(request.user)
        return render(request, "admintemplate/update.html", {'form':form})

@login_required
def updateSkill(request, pk):
    skill = UserSkill.objects.filter(id=pk, custom_user=request.user).first()
    if not skill:
        messages.error(request, "Yetkinlik bulunamadı.")
        return redirect("listingSkill")

    if request.method == "POST":
        form = TeacherSkillForm(request.POST, instance=skill, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Yetkinlik güncellendi.")
            return redirect("listingSkill")
    else:
        form = TeacherSkillForm(instance=skill, user=request.user)

    return render(request, "admintemplate/update.html", {'form': form})

@login_required
def updateEducation(request, pk):
    education = UserEducation.objects.filter(id=pk, custom_user=request.user).first()
    if not education:
        messages.error(request, "Eğitim kaydı bulunamadı.")
        return redirect("listingEducation")

    if request.method == "POST":
        form = TeacherEducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, "Eğitim bilgisi güncellendi.")
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
        form = TeacherWorkForm(request.POST, instance=work)
        if form.is_valid():
            form.save()
            return redirect("listingWork")
    else:
        form = TeacherWorkForm(instance=work)
        return render(request, "admintemplate/update.html", {'form': form})
    
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
def deleteAward(request, pk):
    award = UserAwards.objects.filter(id = pk).first()
    award.delete()
    return redirect("listingAward")

# LOGOUT

@login_required
def loginout(request):
    if request.user.is_authenticated:
        CustomUser.objects.filter(pk=request.user.pk).update(last_seen=None)
    logout(request)
    messages.success(request, "Başarıyla çıkış yapıldı")
    return redirect("login")

@ensure_csrf_cookie
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
                    messages.success(request, 'Giriş başarılı!')
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Geçersiz şifre!')
            except AdminUser.DoesNotExist:
                messages.error(request, 'Kullanıcı bulunamadı!')
    else:
        form = AdminLoginForm()
    
    return render(request, 'admintemplate/admin-login.html', {'form': form})

def admin_logout(request):
    if 'admin_id' in request.session:
        del request.session['admin_id']
        messages.success(request, "Çıkış başarılı")
    return redirect('admin_panel_login')

def admin_dashboard(request):
    if 'admin_id' not in request.session:
        return redirect('admin_panel_login')
        
    users = CustomUser.objects.all()
    course_centers = CourseCenter.objects.all()
    presence = get_active_user_snapshot()

    context = {
        'users': users,
        'course_centers': course_centers,
        'total_users': users.count(),
        'total_course_centers': course_centers.count(),
        'active_teachers': presence['active_teachers'],
        'active_course_centers': presence['active_course_centers'],
        'active_teacher_ids': {int(user_id) for user_id in presence['teachers']},
        'active_course_center_ids': {
            int(course_center_id)
            for course_center_id in presence['course_centers']
        },
    }
    
    return render(request, "admintemplate/admin-dashboard.html", context)


def admin_active_users_api(request):
    if 'admin_id' not in request.session:
        return JsonResponse({'error': 'unauthorized'}, status=403)

    return JsonResponse(get_active_user_snapshot())

def admin_user_detail(request, user_id):
    if 'admin_id' not in request.session:
        return redirect('admin_panel_login')
        
    user = get_object_or_404(CustomUser, id=user_id)
    skills = UserSkill.objects.filter(custom_user=user)
    educations = UserEducation.objects.filter(custom_user=user)
    experiences = UserExperience.objects.filter(custom_user=user)
    services = UserServices.objects.filter(custom_user=user)
    works = UserWorks.objects.filter(custom_user=user)
    awards = UserAwards.objects.filter(custom_user=user)
    
    context = {
        'user': user,
        'skills': skills,
        'educations': educations,
        'experiences': experiences,
        'services': services,
        'works': works,
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