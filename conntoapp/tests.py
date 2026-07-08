from datetime import date
from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import get_user_model
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


class TeacherSearchTests(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(
            username='m1@test.com', email='m1@test.com', password='p',
            fullname='Matematik Öğretmen', gender='MALE', birth_date=date(1985, 5, 5),
            branch='matematik', experience_years='5-10', city='ankara',
        )
        User.objects.create_user(
            username='f1@test.com', email='f1@test.com', password='p',
            fullname='Fizik Öğretmen', gender='FEMALE', birth_date=date(1988, 3, 3),
            branch='fizik', experience_years='3-5', city='istanbul',
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ogretmenim.com')

    def test_search_no_filter_redirects(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 302)

    def test_search_by_branch(self):
        response = self.client.get(reverse('search'), {'branch': 'matematik'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Matematik Öğretmen')
        self.assertNotContains(response, 'Fizik Öğretmen')

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

    def test_usersite_index(self):
        response = self.client.get(reverse('usersite_home', kwargs={'pk': self.teacher.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public Öğretmen')
        self.assertContains(response, 'ogretmenim.com')

    def test_usersite_about(self):
        response = self.client.get(reverse('about', kwargs={'pk': self.teacher.id}))
        self.assertEqual(response.status_code, 200)

    def test_usersite_credentials(self):
        response = self.client.get(reverse('credentials', kwargs={'pk': self.teacher.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Uzun biyografi metni')

    def test_usersite_invalid_pk_renders_with_none_user(self):
        """Bilinen sorun: geçersiz pk ile user=None, template patlayabilir."""
        response = self.client.get(reverse('usersite_home', kwargs={'pk': 99999}))
        self.assertIn(response.status_code, [200, 500])

    def test_get_user_increments_view(self):
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

    def test_admin_dashboard_requires_session(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)


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
            'city': 'ankara',
            'district': 'cankaya',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_register_form_rejects_invalid_district_for_city(self):
        from conntoapp.forms import TeacherRegisterForm
        form = TeacherRegisterForm(data={
            'fullname': 'Yeni Ogretmen',
            'password': 'testpass123',
            'email': 'yeni2@test.com',
            'gender': 'MALE',
            'birth_date': '1995-05-10',
            'branch': 'matematik',
            'city': 'ankara',
            'district': 'kadikoy',
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
            'city': 'izmir',
            'district': 'karsiyaka',
            'checkBox': 'on',
        })
        self.assertRedirects(response, reverse('login'))
        user = User.objects.get(email='ilce@test.com')
        self.assertEqual(user.city, 'izmir')
        self.assertEqual(user.district, 'karsiyaka')

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
