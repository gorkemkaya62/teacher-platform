from django.utils import timezone

from .models import CourseCenter, CustomUser
from .user_presence import should_update_presence


class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._touch_presence(request)
        return self.get_response(request)

    def _touch_presence(self, request):
        now = timezone.now()

        if request.user.is_authenticated:
            if should_update_presence(request.user.last_seen):
                CustomUser.objects.filter(pk=request.user.pk).update(last_seen=now)
            return

        course_center_id = request.session.get('course_center_id')
        if not course_center_id or not request.session.get('is_course_center'):
            return

        course_center = CourseCenter.objects.filter(pk=course_center_id).only('last_seen').first()
        if not course_center:
            return

        if should_update_presence(course_center.last_seen):
            CourseCenter.objects.filter(pk=course_center_id).update(last_seen=now)
