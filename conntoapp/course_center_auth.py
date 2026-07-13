from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


def redirect_if_not_course_center(request):
    if request.session.get('course_center_id'):
        return None
    messages.info(
        request,
        'Öğretmen profillerini görmek için üye olmalısınız.',
    )
    return redirect(f"{reverse('register')}?type=course_center")


def redirect_if_cannot_view_usersite(request, pk):
    if request.session.get('course_center_id'):
        return None
    if request.user.is_authenticated and request.user.pk == pk:
        return None
    if request.user.is_authenticated:
        messages.info(
            request,
            'Başka öğretmen profillerini görmek için kurs merkezi üyeliği gerekir.',
        )
        return redirect('addItems')
    messages.info(
        request,
        'Öğretmen profillerini görmek için üye olmalısınız.',
    )
    return redirect(f"{reverse('register')}?type=course_center")


def redirect_if_not_course_center_member(request):
    if request.session.get('course_center_id'):
        return None
    messages.error(request, 'Profilinizi görmek için kurs merkezi olarak giriş yapmalısınız.')
    return redirect('login')
