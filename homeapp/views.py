from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from conntoapp.models import CustomUser, CourseCenter
from conntoapp.choices import TeacherChoices, CustomUserChoices
from conntoapp.city_coordinates import CITY_COORDINATES
from conntoapp.course_center_auth import (
    redirect_if_not_course_center,
    redirect_if_not_course_center_member,
)


def _get_course_center_id(request):
    return request.session.get('course_center_id')


def _build_teacher_cards(teachers):
    return [{'teacher': teacher} for teacher in teachers]


def _map_teachers_payload(request, teachers):
    is_course_center_view = bool(_get_course_center_id(request))
    payload = []
    for teacher in teachers:
        payload.append({
            'id': teacher.id,
            'name': teacher.fullname,
            'city': teacher.city,
            'cityLabel': teacher.get_city_display(),
            'branch': teacher.get_branch_display(),
            'image': teacher.image.url,
            'profileUrl': (
                reverse('getUser', args=[teacher.id])
                if is_course_center_view
                else f"{reverse('register')}?type=course_center"
            ),
        })
    return payload


def _is_checkbox_checked(request, name):
    value = request.GET.get(name)
    return value in ('on', 'true', '1', 'yes')


def _selected_work_schedule_filters(request):
    works_full_time = _is_checkbox_checked(request, 'works_full_time')
    works_part_time = _is_checkbox_checked(request, 'works_part_time')

    legacy_schedule = request.GET.get('work_schedule', '')
    if legacy_schedule == 'tam_zamanli':
        works_full_time = True
    elif legacy_schedule == 'yari_zamanli':
        works_part_time = True
    elif legacy_schedule == 'her_ikisi':
        works_full_time = True
        works_part_time = True

    return works_full_time, works_part_time


def _build_work_schedule_filter(works_full_time, works_part_time):
    if not works_full_time and not works_part_time:
        return Q()

    schedule_filter = Q()
    if works_full_time:
        schedule_filter |= Q(work_schedule__in=['tam_zamanli', 'her_ikisi'])
    if works_part_time:
        schedule_filter |= Q(work_schedule__in=['yari_zamanli', 'her_ikisi'])
    return schedule_filter


def _listing_context(request, teachers, **extra):
    context = {
        'teacher_cards': _build_teacher_cards(teachers),
        'is_course_center_view': bool(_get_course_center_id(request)),
        'branches': TeacherChoices.BRANCH_CHOICES,
        'experiences': TeacherChoices.EXPERIENCE_CHOICES,
        'cities': CustomUserChoices.TURKISH_CITIES,
        'genders': CustomUserChoices.GENDER_CHOICES,
        'map_teachers': _map_teachers_payload(request, teachers),
        'city_coordinates': CITY_COORDINATES,
    }
    context.update(extra)
    return context


def home(request):
    popular_branch_keys = [
        'bilgisayar', 'matematik', 'ingilizce', 'turkce', 'fizik', 'kimya',
    ]
    branch_map = dict(TeacherChoices.BRANCH_CHOICES)
    popular_branches = [
        {'value': key, 'label': branch_map[key]}
        for key in popular_branch_keys
        if key in branch_map
    ]
    works_full_time, works_part_time = _selected_work_schedule_filters(request)
    context = {
        'branches': TeacherChoices.BRANCH_CHOICES,
        'experiences': TeacherChoices.EXPERIENCE_CHOICES,
        'cities': CustomUserChoices.TURKISH_CITIES,
        'genders': CustomUserChoices.GENDER_CHOICES,
        'popular_branches': popular_branches,
        'selected_branch': request.GET.get('branch', ''),
        'selected_experience': request.GET.get('experience', ''),
        'selected_works_full_time': works_full_time,
        'selected_works_part_time': works_part_time,
        'selected_city': request.GET.get('city', ''),
        'selected_district': request.GET.get('district', ''),
        'selected_gender': request.GET.get('gender', ''),
    }
    return render(request, "home.html", context)


def searchTeacher(request):
    branch = request.GET.get("branch", "")
    experience = request.GET.get("experience", "")
    works_full_time, works_part_time = _selected_work_schedule_filters(request)
    city = request.GET.get("city", "")
    district = request.GET.get("district", "")
    gender = request.GET.get("gender", "")

    filters = Q()
    if branch:
        filters &= Q(branch=branch)
    if experience:
        filters &= Q(experience_years=experience)
    schedule_filter = _build_work_schedule_filter(works_full_time, works_part_time)
    if schedule_filter:
        filters &= schedule_filter
    if city:
        filters &= Q(city=city)
    if district and city:
        filters &= Q(district=district)
    if gender:
        filters &= Q(gender=gender)

    teachers = (
        CustomUser.objects.filter(filters)
        .order_by('fullname', 'id')
        .distinct()
    )

    return render(request, "listing.html", _listing_context(
        request,
        teachers,
        selected_branch=branch,
        selected_experience=experience,
        selected_works_full_time=works_full_time,
        selected_works_part_time=works_part_time,
        selected_city=city,
        selected_district=district if city else '',
        selected_gender=gender,
    ))


def listing(request):
    return render(request, "listing.html", _listing_context(request, []))


def course_center_profile(request):
    redirect_response = redirect_if_not_course_center_member(request)
    if redirect_response:
        return redirect_response

    course_center = get_object_or_404(
        CourseCenter,
        id=request.session['course_center_id'],
    )

    if request.method == 'POST':
        image = request.FILES.get('image')
        if not image:
            messages.error(request, 'Lütfen bir fotoğraf seçin.')
            return redirect('course_center_profile')

        course_center.image = image
        course_center.save()
        messages.success(request, 'Profil bilgileriniz başarıyla güncellendi.', extra_tags='popup')
        return redirect('course_center_profile')

    return render(request, 'course_center_profile.html', {
        'course_center': course_center,
    })


def getUser(request, pk):
    redirect_response = redirect_if_not_course_center(request)
    if redirect_response:
        return redirect_response

    user = CustomUser.objects.filter(id=pk).first()
    if user:
        user.view = user.view + 1
        user.save()
        return redirect("usersite_home", pk=user.id)
    return redirect("home")
