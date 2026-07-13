from datetime import timedelta

from django.utils import timezone

ACTIVE_USER_WINDOW = timedelta(minutes=5)
PRESENCE_UPDATE_INTERVAL = timedelta(seconds=60)


def is_recently_active(last_seen):
    if not last_seen:
        return False
    return timezone.now() - last_seen <= ACTIVE_USER_WINDOW


def should_update_presence(last_seen):
    if not last_seen:
        return True
    return timezone.now() - last_seen >= PRESENCE_UPDATE_INTERVAL


def get_active_teacher_ids():
    cutoff = timezone.now() - ACTIVE_USER_WINDOW
    from .models import CustomUser

    return set(
        CustomUser.objects.filter(last_seen__gte=cutoff).values_list('id', flat=True)
    )


def get_active_course_center_ids():
    cutoff = timezone.now() - ACTIVE_USER_WINDOW
    from .models import CourseCenter

    return set(
        CourseCenter.objects.filter(last_seen__gte=cutoff).values_list('id', flat=True)
    )


def get_active_user_snapshot():
    active_teacher_ids = get_active_teacher_ids()
    active_course_center_ids = get_active_course_center_ids()

    return {
        'active_teachers': len(active_teacher_ids),
        'active_course_centers': len(active_course_center_ids),
        'teachers': {str(user_id): True for user_id in active_teacher_ids},
        'course_centers': {
            str(course_center_id): True
            for course_center_id in active_course_center_ids
        },
    }
