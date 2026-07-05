from django.conf import settings
from .models import CourseCenter
from .choices import TeacherChoices, CustomUserChoices


def site_processor(request):
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_TAGLINE': settings.SITE_TAGLINE,
        'header_branches': TeacherChoices.BRANCH_CHOICES,
        'header_cities': CustomUserChoices.TURKISH_CITIES,
    }


def course_center_processor(request):
    if 'course_center_id' in request.session:
        try:
            course_center = CourseCenter.objects.get(id=request.session['course_center_id'])
            return {
                'current_course_center': course_center,
                'is_course_center_view': True,
            }
        except CourseCenter.DoesNotExist:
            del request.session['course_center_id']
            del request.session['is_course_center']
    return {
        'current_course_center': None,
        'is_course_center_view': False,
    }
