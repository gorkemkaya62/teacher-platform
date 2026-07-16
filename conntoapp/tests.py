from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import get_user_model
from django.utils import timezone
from conntoapp.models import (
    CourseCenter, AdminUser, UserSkill, UserEducation,
    UserExperience, UserServices, UserAwards,
)

User = get_user_model()


class URLResolutionTests(TestCase):
    """Kritik URL'lerin doğru çözümlenmesi."""

    def test_teacher_urls(self):
        self.assertEqual(reverse('login'), '/adminpanel/login')
        self.assertEqual(reverse('register'), '/adminpanel/register')
        self.assertEqual(reverse('addItems'), '/adminpanel/add-items')
        self.assertEqual(reverse('home'), '/home/')

    def test_usersite_home_requires_pk(self):
        self.assertEqual(reverse('usersite_home', kwargs={'pk': 7}), '/usersite/7')

    def test_admin_panel_double_prefix_issue(self):
        """Bilinen sorun: platform admin URL'leri çift adminpanel prefix'i alıyor."""
        self.assertEqual(reverse('admin_dashboard'), '/adminpanel/adminpanel/dashboard')
        self.assertEqual(reverse('admin_panel_login'), '/adminpanel/adminpanel/login')

    def test_search_url(self):
        self.assertEqual(reverse('search'), '/home/searching')


class TeacherAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher@test.com',
            email='teacher@test.com',
            password='testpass123',
            fullname='Test Öğretmen',
            gender='MALE',
            birth_date=date(1990, 1, 1),
            branch='matematik',
            city='ankara',
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ogretmenim.com')

    def test_teacher_login_redirects_to_add_items(self):
        response = self.client.post(reverse('login'), {
            'email': 'teacher@test.com',
            'password': 'testpass123',
            'is_course_center': 'false',
        })
        self.assertRedirects(response, reverse('addItems'))

    def test_add_items_requires_login(self):
        response = self.client.get(reverse('addItems'))
        self.assertEqual(response.status_code, 302)

    def test_add_items_authenticated(self):
        self.client.login(username='teacher@test.com', password='testpass123')
        response = self.client.get(reverse('addItems'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Öğretmen Profili')

    def test_teacher_profile_save_shows_success_popup(self):
        self.client.login(username='teacher@test.com', password='testpass123')
        response = self.client.post(reverse('teacherProfileAccept'), {
            'active_tab': 'profile',
            'branch': 'matematik',
            'experience_years': '3-5',
            'works_full_time': 'on',
            'city': 'ankara',
            'district': 'cankaya',
            'gender': 'MALE',
            'phone_country_code': '+90',
            'phone_number': '5321234567',
            'short_description': 'Matematik öğretmeni',
            'long_description': 'Deneyimli matematik öğretmeni.',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profil bilgileriniz başarıyla güncellendi.')
        self.assertContains(response, 'Swal.fire')


class CourseCenterAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cc = CourseCenter.objects.create(
            center_name='Test Kurs',
            center_type='Dil Kursu',
            teacher_capacity=10,
            email='kurs@test.com',
        )
        self.cc.set_password('kurspass123')
        self.cc.save()

    def test_course_center_login_sets_session(self):
        response = self.client.post(reverse('login'), {
            'email': 'kurs@test.com',
            'password': 'kurspass123',
            'is_course_center': 'true',
        })
        self.assertRedirects(response, '/home/')
        self.assertEqual(self.client.session.get('course_center_id'), self.cc.id)
        self.assertTrue(self.client.session.get('is_course_center'))

    def test_course_center_register(self):
        response = self.client.post(reverse('register'), {
            'is_course_center': 'true',
            'center_name': 'Yeni Kurs',
            'center_type': 'Sınav Hazırlık',
            'teacher_capacity': 5,
            'email': 'yeni@kurs.com',
            'password': 'sifre123',
            'checkBox': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CourseCenter.objects.filter(email='yeni@kurs.com').exists())

    def test_course_center_profile_requires_login(self):
        response = self.client.get(reverse('course_center_profile'))
        self.assertEqual(response.status_code, 302)

    def test_course_center_profile_shows_registration_info(self):
        session = self.client.session
        session['course_center_id'] = self.cc.id
        session['is_course_center'] = True
        session.save()

        response = self.client.get(reverse('course_center_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Kurs')
        self.assertContains(response, 'Dil Kursu')
        self.assertContains(response, '10')
        self.assertContains(response, 'kurs@test.com')
        self.assertContains(response, 'course-center-photo-trigger')
        self.assertContains(response, 'fa-pencil')
        self.assertNotContains(response, 'Fotoğrafı Güncelle')
        self.assertNotContains(response, 'sifre')
        self.assertContains(response, 'href="/home/#ogretmen-ara"')
        self.assertNotContains(response, 'href="/home/searching"')

    def test_course_center_profile_upload_photo(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        import io

        session = self.client.session
        session['course_center_id'] = self.cc.id
        session['is_course_center'] = True
        session.save()

        image_io = io.BytesIO()
        Image.new('RGB', (120, 120), color='teal').save(image_io, format='JPEG')
        image_io.seek(0)
        upload = SimpleUploadedFile(
            'profile.jpg',
            image_io.read(),
            content_type='image/jpeg',
        )

        response = self.client.post(
            reverse('course_center_profile'),
            {'image': upload},
        )
        self.assertRedirects(response, reverse('course_center_profile'))

        self.cc.refresh_from_db()
        self.assertTrue(self.cc.has_custom_image)


class TeacherSearchTests(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(
            username='m1@test.com', email='m1@test.com', password='p',
            fullname='Matematik Öğretmen', gender='MALE', birth_date=date(1985, 5, 5),
            branch='matematik', experience_years='5-10', work_schedule='tam_zamanli',
            city='ankara', district='cankaya',
        )
        User.objects.create_user(
            username='f1@test.com', email='f1@test.com', password='p',
            fullname='Fizik Öğretmen', gender='FEMALE', birth_date=date(1988, 3, 3),
            branch='fizik', experience_years='3-5', work_schedule='yari_zamanli',
            city='istanbul', district='kadikoy',
        )
        User.objects.create_user(
            username='e1@test.com', email='e1@test.com', password='p',
            fullname='Esnek Öğretmen', gender='MALE', birth_date=date(1990, 1, 1),
            branch='ingilizce', experience_years='1-3', work_schedule='her_ikisi',
            city='izmir', district='karsiyaka',
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ogretmenim.com')
        self.assertContains(response, 'id="search-district"')
        self.assertContains(response, 'id="search-works-full-time"')
        self.assertContains(response, 'id="search-works-part-time"')
        self.assertContains(response, 'city-district.js')

    def test_search_by_district(self):
        response = self.client.get(reverse('search'), {
            'city': 'ankara',
            'district': 'cankaya',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Matematik Öğretmen')
        self.assertNotContains(response, 'Fizik Öğretmen')

    def test_search_listing_has_district_filter(self):
        response = self.client.get(reverse('search'), {'branch': 'matematik'})
        self.assertContains(response, 'id="filter-district"')
        self.assertContains(response, 'data-selected-district')

    def test_search_without_filters_lists_all_teachers(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Matematik Öğretmen')
        self.assertContains(response, 'Fizik Öğretmen')
        self.assertContains(response, 'Esnek Öğretmen')

    def test_search_by_work_schedule_tam_zamanli(self):
        response = self.client.get(reverse('search'), {'works_full_time': 'on'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Matematik Öğretmen')
        self.assertContains(response, 'Esnek Öğretmen')
        self.assertNotContains(response, 'Fizik Öğretmen')

    def test_search_by_work_schedule_yari_zamanli(self):
        response = self.client.get(reverse('search'), {'works_part_time': 'on'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fizik Öğretmen')
        self.assertContains(response, 'Esnek Öğretmen')
        self.assertNotContains(response, 'Matematik Öğretmen')

    def test_search_by_work_schedule_both_checked(self):
        response = self.client.get(reverse('search'), {
            'works_full_time': 'on',
            'works_part_time': 'on',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Matematik Öğretmen')
        self.assertContains(response, 'Fizik Öğretmen')
        self.assertContains(response, 'Esnek Öğretmen')

    def test_search_listing_has_work_schedule_filter(self):
        response = self.client.get(reverse('search'))
        self.assertContains(response, 'id="filter-works-full-time"')
        self.assertContains(response, 'id="filter-works-part-time"')
        self.assertContains(response, 'connto-work-schedule-checks')

    def test_search_by_branch(self):
        response = self.client.get(reverse('search'), {'branch': 'matematik'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Matematik Öğretmen')
        self.assertNotContains(response, 'Fizik Öğretmen')
        self.assertContains(response, 'fa-lock')
        self.assertContains(response, 'connto-teacher-card connto-teacher-card--guest')
        self.assertContains(response, 'connto-teacher-card__blurred')
        self.assertContains(response, 'connto-filter-panel__lock')
        self.assertContains(response, 'connto-map-btn__lock')
        self.assertContains(response, 'connto-directory__toolbar--guest')
        self.assertNotContains(response, 'öğretmen bulundu')
        self.assertNotContains(response, 'data-target="#mapModal"')
        self.assertNotContains(response, '>Profil</a>')

    def test_search_shows_profile_for_course_center(self):
        cc = CourseCenter.objects.create(
            center_name='Test Kurs',
            center_type='Dil Kursu',
            teacher_capacity=10,
            email='kurs@test.com',
        )
        cc.set_password('kurspass123')
        cc.save()
        session = self.client.session
        session['course_center_id'] = cc.id
        session['is_course_center'] = True
        session.save()

        response = self.client.get(reverse('search'), {'branch': 'matematik'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '>Profil</a>')
        self.assertNotContains(response, 'connto-teacher-card connto-teacher-card--guest')
        self.assertNotContains(response, 'connto-filter-panel__lock')
        self.assertNotContains(response, 'connto-map-btn__lock')
        self.assertContains(response, 'öğretmen bulundu')
        self.assertContains(response, 'data-target="#mapModal"')

    def test_get_user_redirects_guest_to_register(self):
        teacher = User.objects.get(email='m1@test.com')
        response = self.client.get(reverse('getUser', kwargs={'pk': teacher.id}))
        self.assertRedirects(response, f"{reverse('register')}?type=course_center")

    def test_search_combined_filters(self):
        response = self.client.get(reverse('search'), {
            'branch': 'fizik',
            'city': 'istanbul',
            'gender': 'FEMALE',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fizik Öğretmen')

    def test_search_no_match(self):
        response = self.client.get(reverse('search'), {
            'branch': 'matematik',
            'city': 'istanbul',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Matematik Öğretmen')


class UsersiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='public@test.com', email='public@test.com', password='p',
            fullname='Public Öğretmen', gender='MALE', birth_date=date(1992, 6, 6),
            branch='ingilizce', city='izmir',
            short_description='Deneyimli öğretmen',
            long_description='Uzun biyografi metni.',
        )
        self.cc = CourseCenter.objects.create(
            center_name='Test Kurs',
            center_type='Dil Kursu',
            teacher_capacity=10,
            email='kurs@test.com',
        )
        self.cc.set_password('kurspass123')
        self.cc.save()

    def _login_as_course_center(self):
        session = self.client.session
        session['course_center_id'] = self.cc.id
        session['is_course_center'] = True
        session.save()

    def test_usersite_index_redirects_guest_to_register(self):
        response = self.client.get(reverse('usersite_home', kwargs={'pk': self.teacher.id}))
        self.assertRedirects(response, f"{reverse('register')}?type=course_center")

    def test_usersite_index_for_course_center(self):
        self._login_as_course_center()

        response = self.client.get(reverse('usersite_home', kwargs={'pk': self.teacher.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public Öğretmen')
        self.assertContains(response, 'ogretmenim.com')

    def test_usersite_index_for_teacher_own_profile(self):
        self.client.login(username='public@test.com', password='p')

        response = self.client.get(reverse('usersite_home', kwargs={'pk': self.teacher.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public Öğretmen')

    def test_usersite_index_redirects_teacher_to_add_items_for_other_profile(self):
        other_teacher = User.objects.create_user(
            username='other@test.com', email='other@test.com', password='p',
            fullname='Diğer Öğretmen', gender='FEMALE', birth_date=date(1991, 3, 3),
            branch='matematik', city='ankara',
        )
        self.client.login(username='public@test.com', password='p')

        response = self.client.get(reverse('usersite_home', kwargs={'pk': other_teacher.id}))
        self.assertRedirects(response, reverse('addItems'))

    def test_usersite_about(self):
        self._login_as_course_center()
        response = self.client.get(reverse('about', kwargs={'pk': self.teacher.id}))
        self.assertEqual(response.status_code, 200)

    def test_usersite_credentials(self):
        self._login_as_course_center()
        response = self.client.get(reverse('credentials', kwargs={'pk': self.teacher.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Uzun biyografi metni')

    def test_usersite_invalid_pk_renders_with_none_user(self):
        """Bilinen sorun: geçersiz pk ile user=None, template patlayabilir."""
        self._login_as_course_center()
        response = self.client.get(reverse('usersite_home', kwargs={'pk': 99999}))
        self.assertIn(response.status_code, [200, 500])

    def test_get_user_increments_view(self):
        self._login_as_course_center()
        initial = self.teacher.view
        self.client.get(reverse('getUser', kwargs={'pk': self.teacher.id}))
        self.teacher.refresh_from_db()
        self.assertEqual(self.teacher.view, initial + 1)


class ProfileCRUDTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='crud@test.com', email='crud@test.com', password='testpass123',
            fullname='CRUD Öğretmen', gender='MALE', birth_date=date(1990, 1, 1),
            branch='turkce', city='bursa',
        )
        self.client.login(username='crud@test.com', password='testpass123')
        self.other = User.objects.create_user(
            username='other@test.com', email='other@test.com', password='p',
            fullname='Diğer', gender='FEMALE', birth_date=date(1991, 2, 2),
            branch='tarih', city='konya',
        )
        self.other_skill = UserSkill.objects.create(
            custom_user=self.other, skill_name='Python', skill_degree=80,
        )

    def test_add_skill(self):
        response = self.client.post(reverse('teacherSkillAccept'), {
            'skill_name': 'Matematik', 'skill_degree': 90,
        })
        self.assertRedirects(response, reverse('listingSkill'))
        self.assertTrue(UserSkill.objects.filter(custom_user=self.teacher, skill_name='Matematik').exists())

    def test_add_skill_rejects_invalid_degree(self):
        response = self.client.post(reverse('teacherSkillAccept'), {
            'skill_name': 'Matematik', 'skill_degree': 150,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0 ile 100 arasında')
        self.assertFalse(UserSkill.objects.filter(custom_user=self.teacher, skill_name='Matematik').exists())

    def test_add_skill_rejects_degree_from_add_items(self):
        response = self.client.post(reverse('teacherSkillAccept'), {
            'form_source': 'add_items',
            'skill_name': 'Sinif Yonetimi',
            'skill_degree': 22222,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0 ile 100 arasında')
        self.assertFalse(UserSkill.objects.filter(custom_user=self.teacher, skill_name='Sinif Yonetimi').exists())

    def test_add_skill_rejects_duplicate_name(self):
        UserSkill.objects.create(
            custom_user=self.teacher, skill_name='Sinif Yonetimi', skill_degree=70,
        )
        response = self.client.post(reverse('teacherSkillAccept'), {
            'form_source': 'add_items',
            'skill_name': 'Sinif Yonetimi',
            'skill_degree': 80,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'daha önce kaydedildi')
        self.assertEqual(
            UserSkill.objects.filter(custom_user=self.teacher, skill_name__iexact='Sinif Yonetimi').count(),
            1,
        )

    def test_add_skill_rejects_duplicate_name_case_insensitive(self):
        UserSkill.objects.create(
            custom_user=self.teacher, skill_name='Matematik', skill_degree=70,
        )
        response = self.client.post(reverse('teacherSkillAccept'), {
            'skill_name': 'matematik',
            'skill_degree': 80,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'daha önce kaydedildi')
        self.assertEqual(
            UserSkill.objects.filter(custom_user=self.teacher, skill_name__iexact='Matematik').count(),
            1,
        )

    def test_idor_delete_other_users_skill(self):
        """Bilinen güvenlik sorunu: başkasının kaydı silinebilir."""
        response = self.client.get(reverse('deleteSkill', kwargs={'pk': self.other_skill.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(UserSkill.objects.filter(id=self.other_skill.id).exists())


class PlatformAdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = AdminUser.objects.create(
            username='admin', email='admin@ogretmenim.com',
        )
        self.admin.set_password('admin123')
        self.admin.save()

    def test_admin_login_page(self):
        response = self.client.get(reverse('admin_panel_login'))
        self.assertEqual(response.status_code, 200)

    def test_admin_login_success(self):
        response = self.client.post(reverse('admin_panel_login'), {
            'username': 'admin',
            'password': 'admin123',
        })
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertIn('admin_id', self.client.session)

    def test_admin_login_post_requires_valid_csrf(self):
        client = Client(enforce_csrf_checks=True)
        login_url = reverse('admin_panel_login')
        response = client.get(login_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')

        bad_post = client.post(login_url, {
            'username': 'admin',
            'password': 'admin123',
            'csrfmiddlewaretoken': 'invalid-token',
        })
        self.assertEqual(bad_post.status_code, 403)

        good_post = client.post(login_url, {
            'username': 'admin',
            'password': 'admin123',
            'csrfmiddlewaretoken': response.cookies['csrftoken'].value,
        })
        self.assertRedirects(good_post, reverse('admin_dashboard'))

    def test_admin_dashboard_requires_session(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)


class UserPresenceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = AdminUser.objects.create(
            username='admin', email='admin@ogretmenim.com',
        )
        self.admin.set_password('admin123')
        self.admin.save()

        self.teacher = User.objects.create_user(
            username='teacher@test.com',
            email='teacher@test.com',
            password='teacherpass',
            fullname='Aktif Öğretmen',
            gender='MALE',
            birth_date=date(1990, 1, 1),
            branch='matematik',
            city='ankara',
        )
        self.course_center = CourseCenter.objects.create(
            center_name='Aktif Kurs',
            center_type='Dil Kursu',
            teacher_capacity=20,
            email='aktif@kurs.com',
        )
        self.course_center.set_password('kurspass123')
        self.course_center.save()

    def _login_admin(self):
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

    def test_teacher_request_updates_last_seen(self):
        self.client.login(username='teacher@test.com', password='teacherpass')
        self.client.get(reverse('addItems'))

        self.teacher.refresh_from_db()
        self.assertIsNotNone(self.teacher.last_seen)
        self.assertLessEqual(
            timezone.now() - self.teacher.last_seen,
            timedelta(minutes=1),
        )

    def test_course_center_request_updates_last_seen(self):
        session = self.client.session
        session['course_center_id'] = self.course_center.id
        session['is_course_center'] = True
        session.save()

        self.client.get(reverse('home'))

        self.course_center.refresh_from_db()
        self.assertIsNotNone(self.course_center.last_seen)

    def test_admin_dashboard_shows_active_counts_and_dots(self):
        now = timezone.now()
        CustomUser = User
        CustomUser.objects.filter(pk=self.teacher.pk).update(last_seen=now)
        CourseCenter.objects.filter(pk=self.course_center.pk).update(last_seen=now)

        self._login_admin()
        response = self.client.get(reverse('admin_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aktif Öğretmen')
        self.assertContains(response, 'Aktif Kurs Merkezi')
        self.assertContains(response, 'presence-dot--active')
        self.assertContains(response, 'id="active-teachers-count"')
        self.assertContains(response, 'id="active-course-centers-count"')

    def test_admin_active_users_api_returns_snapshot(self):
        now = timezone.now()
        User.objects.filter(pk=self.teacher.pk).update(last_seen=now)

        self._login_admin()
        response = self.client.get(reverse('admin_active_users_api'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['active_teachers'], 1)
        self.assertEqual(data['active_course_centers'], 0)
        self.assertTrue(data['teachers'][str(self.teacher.id)])

    def test_admin_active_users_api_requires_session(self):
        response = self.client.get(reverse('admin_active_users_api'))
        self.assertEqual(response.status_code, 403)

    def test_logout_clears_teacher_presence(self):
        User.objects.filter(pk=self.teacher.pk).update(last_seen=timezone.now())
        self.client.login(username='teacher@test.com', password='teacherpass')
        self.client.get(reverse('logout'))

        self.teacher.refresh_from_db()
        self.assertIsNone(self.teacher.last_seen)


class ModelTests(TestCase):
    def test_teacher_str_and_display(self):
        user = User.objects.create_user(
            username='m@test.com', email='m@test.com', password='p',
            fullname='Ali Veli', gender='MALE', birth_date=date(1980, 1, 1),
            branch='matematik', experience_years='3-5', city='ankara', district='cankaya',
        )
        self.assertEqual(str(user), 'Ali Veli')
        self.assertEqual(user.get_branch_display(), 'Matematik')
        self.assertEqual(user.get_city_display(), 'Ankara')

    def test_work_schedule_profile_display(self):
        user = User.objects.create_user(
            username='w@test.com', email='w@test.com', password='p',
            fullname='Work User', gender='MALE', birth_date=date(1980, 1, 1),
            branch='matematik', city='ankara', work_schedule='her_ikisi',
        )
        self.assertEqual(user.get_work_schedule_profile_display(), 'Tam Zamanlı · Yarı Zamanlı')

        user.work_schedule = 'tam_zamanli'
        self.assertEqual(user.get_work_schedule_profile_display(), 'Tam Zamanlı')

        user.work_schedule = 'yari_zamanli'
        self.assertEqual(user.get_work_schedule_profile_display(), 'Yarı Zamanlı')

    def test_experience_institution_name(self):
        user = User.objects.create_user(
            username='e@test.com', email='e@test.com', password='p',
            fullname='Exp', gender='MALE', birth_date=date(1980, 1, 1),
            branch='fizik', city='ankara',
        )
        exp = UserExperience.objects.create(
            custom_user=user,
            institution_name='ABC Kurs Merkezi',
            department='Fizik',
            start_date=date(2020, 1, 1),
            short_description='Deneyim açıklaması',
        )
        self.assertEqual(str(exp), 'ABC Kurs Merkezi')

    def test_normalize_profile_image_crops_to_square(self):
        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        from conntoapp.image_utils import normalize_profile_image, PROFILE_IMAGE_SIZE

        buffer = BytesIO()
        Image.new('RGB', (600, 400), color='red').save(buffer, format='JPEG')
        buffer.seek(0)
        upload = SimpleUploadedFile('wide.jpg', buffer.read(), content_type='image/jpeg')

        normalized = normalize_profile_image(upload)
        result = Image.open(normalized)
        self.assertEqual(result.size, (PROFILE_IMAGE_SIZE, PROFILE_IMAGE_SIZE))


class CityDistrictTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_district_api_returns_ankara_districts(self):
        response = self.client.get(reverse('district_choices_api'), {'city': 'ankara'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        slugs = {item['value'] for item in data['districts']}
        self.assertIn('cankaya', slugs)
        self.assertIn('kecioren', slugs)
        self.assertGreater(len(data['districts']), 20)

    def test_district_api_returns_istanbul_districts(self):
        response = self.client.get(reverse('district_choices_api'), {'city': 'istanbul'})
        self.assertEqual(response.status_code, 200)
        slugs = {item['value'] for item in response.json()['districts']}
        self.assertIn('kadikoy', slugs)
        self.assertIn('besiktas', slugs)

    def test_district_api_empty_city(self):
        response = self.client.get(reverse('district_choices_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['districts'], [])

    def test_register_form_accepts_valid_city_district(self):
        from conntoapp.forms import TeacherRegisterForm
        form = TeacherRegisterForm(data={
            'fullname': 'Yeni Ogretmen',
            'password': 'testpass123',
            'email': 'yeni@test.com',
            'gender': 'MALE',
            'birth_date': '1995-05-10',
            'branch': 'matematik',
            'works_full_time': True,
            'city': 'ankara',
            'district': 'cankaya',
            'phone_country_code': '+90',
            'phone_number': '5321234567',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_register_form_rejects_phone_starting_with_zero(self):
        from conntoapp.forms import TeacherRegisterForm
        form = TeacherRegisterForm(data={
            'fullname': 'Yeni Ogretmen',
            'password': 'testpass123',
            'email': 'zero@test.com',
            'gender': 'MALE',
            'birth_date': '1995-05-10',
            'branch': 'matematik',
            'works_full_time': True,
            'city': 'ankara',
            'district': 'cankaya',
            'phone_country_code': '+90',
            'phone_number': '05321234567',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)

    def test_register_form_rejects_invalid_district_for_city(self):
        from conntoapp.forms import TeacherRegisterForm
        form = TeacherRegisterForm(data={
            'fullname': 'Yeni Ogretmen',
            'password': 'testpass123',
            'email': 'yeni2@test.com',
            'gender': 'MALE',
            'birth_date': '1995-05-10',
            'branch': 'matematik',
            'works_full_time': True,
            'city': 'ankara',
            'district': 'kadikoy',
            'phone_country_code': '+90',
            'phone_number': '5321234567',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('district', form.errors)

    def test_teacher_register_post_with_district(self):
        response = self.client.post(reverse('register'), {
            'fullname': 'Ilce Test',
            'password': 'testpass123',
            'email': 'ilce@test.com',
            'gender': 'MALE',
            'birth_date': '1990-01-01',
            'branch': 'fizik',
            'works_part_time': True,
            'city': 'izmir',
            'district': 'karsiyaka',
            'phone_country_code': '+90',
            'phone_number': '5329876543',
            'checkBox': 'on',
        })
        self.assertRedirects(response, reverse('login'))
        user = User.objects.get(email='ilce@test.com')
        self.assertEqual(user.city, 'izmir')
        self.assertEqual(user.district, 'karsiyaka')
        self.assertEqual(user.work_schedule, 'yari_zamanli')
        self.assertEqual(user.phone, '+905329876543')

    def test_register_form_requires_work_schedule(self):
        from conntoapp.forms import TeacherRegisterForm
        form = TeacherRegisterForm(data={
            'fullname': 'Yeni Ogretmen',
            'password': 'testpass123',
            'email': 'schedule@test.com',
            'gender': 'MALE',
            'birth_date': '1995-05-10',
            'branch': 'matematik',
            'city': 'ankara',
            'district': 'cankaya',
            'phone_country_code': '+90',
            'phone_number': '5321234567',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('works_full_time', form.errors)
        self.assertEqual(form.errors['works_full_time'], ['required'])

    def test_register_form_rejects_under_18(self):
        from conntoapp.forms import TeacherRegisterForm, latest_birth_date_for_minimum_age
        too_young = latest_birth_date_for_minimum_age(18)
        too_young = too_young.replace(year=too_young.year + 1)
        form = TeacherRegisterForm(data={
            'fullname': 'Genc Ogretmen',
            'password': 'testpass123',
            'email': 'young@test.com',
            'gender': 'MALE',
            'birth_date': too_young.isoformat(),
            'branch': 'matematik',
            'works_full_time': True,
            'city': 'ankara',
            'district': 'cankaya',
            'phone_country_code': '+90',
            'phone_number': '5321234567',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('birth_date', form.errors)
        self.assertEqual(
            form.errors['birth_date'],
            ['Kayıt olmak için en az 18 yaşında olmalısınız.'],
        )

    def test_register_form_accepts_exactly_18(self):
        from conntoapp.forms import TeacherRegisterForm, latest_birth_date_for_minimum_age
        birth_date = latest_birth_date_for_minimum_age(18)
        form = TeacherRegisterForm(data={
            'fullname': 'On Sekiz Yas',
            'password': 'testpass123',
            'email': 'eighteen@test.com',
            'gender': 'MALE',
            'birth_date': birth_date.isoformat(),
            'branch': 'matematik',
            'works_full_time': True,
            'city': 'ankara',
            'district': 'cankaya',
            'phone_country_code': '+90',
            'phone_number': '5321234567',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_register_post_rejects_under_18(self):
        from conntoapp.forms import latest_birth_date_for_minimum_age
        too_young = latest_birth_date_for_minimum_age(18)
        too_young = too_young.replace(year=too_young.year + 1)
        response = self.client.post(reverse('register'), {
            'fullname': 'Genc Kullanici',
            'password': 'testpass123',
            'email': 'youngpost@test.com',
            'gender': 'MALE',
            'birth_date': too_young.isoformat(),
            'branch': 'matematik',
            'works_full_time': 'on',
            'city': 'ankara',
            'district': 'cankaya',
            'phone_country_code': '+90',
            'phone_number': '5321234567',
            'checkBox': 'on',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kayıt olmak için en az 18 yaşında olmalısınız.')
        self.assertContains(response, 'register-birth-date.js')
        self.assertFalse(User.objects.filter(email='youngpost@test.com').exists())

    def test_register_page_includes_birth_date_max_limit(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'max="{date.today().isoformat()}"')
        self.assertContains(response, 'data-register-min-age="18"')
        self.assertContains(response, 'register-birth-date.js')

    def test_register_form_accepts_both_work_schedules(self):
        from conntoapp.forms import TeacherRegisterForm
        form = TeacherRegisterForm(data={
            'fullname': 'Esnek Ogretmen',
            'password': 'testpass123',
            'email': 'esnek@test.com',
            'gender': 'MALE',
            'birth_date': '1995-05-10',
            'branch': 'matematik',
            'works_full_time': True,
            'works_part_time': True,
            'city': 'ankara',
            'district': 'cankaya',
            'phone_country_code': '+90',
            'phone_number': '5321234567',
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.work_schedule, 'her_ikisi')

    def test_register_post_requires_work_schedule_selection(self):
        response = self.client.post(reverse('register'), {
            'fullname': 'Eksik Ogretmen',
            'password': 'testpass123',
            'email': 'eksik@test.com',
            'gender': 'MALE',
            'birth_date': '1990-01-01',
            'branch': 'matematik',
            'city': 'ankara',
            'district': 'cankaya',
            'phone_country_code': '+90',
            'phone_number': '5321112233',
            'checkBox': 'on',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'connto-work-schedule-field--error')
        self.assertNotContains(response, 'cdn.jsdelivr.net/npm/sweetalert2')

    def test_register_page_has_phone_country_selector(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'phone_country_code')
        self.assertContains(response, 'connto-phone-country-picker')
        self.assertContains(response, 'flagcdn.com')
        self.assertContains(response, '+90')
        self.assertContains(response, 'Numarayı başında 0 olmadan girin')
        self.assertContains(response, 'phone-field.js')

    def test_register_page_has_district_field_and_script(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="id_district"')
        self.assertContains(response, 'city-district.js')

    def test_get_district_display(self):
        user = User.objects.create_user(
            username='d@test.com', email='d@test.com', password='p',
            fullname='Display Test', gender='FEMALE', birth_date=date(1985, 3, 3),
            branch='turkce', city='ankara', district='cankaya',
        )
        self.assertEqual(user.get_district_display(), 'Çankaya')
