from django.db import models
from django.contrib.auth.models import AbstractUser
from .choices import CustomUserChoices, CustomUserEducationChoices, TeacherChoices
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=100, verbose_name="Ad Soyad")
    twitter = models.CharField(max_length=100, null=True, blank=True, verbose_name="X")
    facebook = models.CharField(max_length=100, null=True, blank=True, verbose_name="Facebook")
    linkedin = models.CharField(max_length=100, null=True, blank=True, verbose_name="LinkedIn")
    instagram = models.CharField(max_length=100, null=True, blank=True, verbose_name="Instagram")
    gender = models.CharField(max_length=6, choices=CustomUserChoices.GENDER_CHOICES, verbose_name="Cinsiyet")
    birth_date = models.DateField(verbose_name="Doğum Tarihi")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefon")
    branch = models.CharField(
        max_length=50,
        choices=TeacherChoices.BRANCH_CHOICES,
        default='matematik',
        verbose_name="Branş",
    )
    experience_years = models.CharField(
        max_length=10,
        choices=TeacherChoices.EXPERIENCE_CHOICES,
        default='0-1',
        verbose_name="Deneyim Süresi",
    )
    work_schedule = models.CharField(
        max_length=20,
        choices=TeacherChoices.WORK_SCHEDULE_CHOICES,
        default='her_ikisi',
        verbose_name="Çalışma Şekli",
    )
    city = models.CharField(max_length=30, choices=CustomUserChoices.TURKISH_CITIES, verbose_name="Şehir")
    district = models.CharField(max_length=50, null=True, blank=True, verbose_name="İlçe")
    job = models.CharField(max_length=20, blank=True, default='')
    short_description = models.CharField(max_length=100, null=True, blank=True, verbose_name="Kısa Tanıtım")
    long_description = models.TextField(max_length=500, null=True, blank=True, verbose_name="Biyografi")
    view = models.IntegerField(default=0)
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name="Son Aktiflik")
    image = models.ImageField(upload_to="images/", default="images/default.jpg", null=False, blank=False, verbose_name="Profil Fotoğrafı")

    class Meta:
        verbose_name = "Öğretmen"
        verbose_name_plural = "Öğretmenler"

    def __str__(self):
        return self.fullname

    def get_district_display(self):
        from .district_data import get_district_label
        if not self.district:
            return ""
        return get_district_label(self.city, self.district)

    def get_work_schedule_profile_display(self):
        labels = []
        if self.work_schedule in ('tam_zamanli', 'her_ikisi'):
            labels.append('Tam Zamanlı')
        if self.work_schedule in ('yari_zamanli', 'her_ikisi'):
            labels.append('Yarı Zamanlı')
        return ' · '.join(labels)


class CourseCenter(models.Model):
    center_name = models.CharField(max_length=100, verbose_name="Kurs Merkezi Adı")
    center_type = models.CharField(max_length=100, verbose_name="Kurs Türü")
    teacher_capacity = models.IntegerField(verbose_name="Öğretmen Kapasitesi")
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name="E-posta")
    password = models.CharField(max_length=128, null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name="Son Aktiflik")
    image = models.ImageField(
        upload_to="course_centers/",
        default="images/default.jpg",
        null=False,
        blank=False,
        verbose_name="Profil Fotoğrafı",
    )

    class Meta:
        verbose_name = "Kurs Merkezi"
        verbose_name_plural = "Kurs Merkezleri"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def has_custom_image(self):
        return bool(self.image and self.image.name != "images/default.jpg")

    def __str__(self):
        return self.center_name


class TeacherRating(models.Model):
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='Öğretmen',
    )
    course_center = models.ForeignKey(
        CourseCenter,
        on_delete=models.CASCADE,
        related_name='teacher_ratings',
        verbose_name='Kurs Merkezi',
    )
    score = models.PositiveSmallIntegerField(verbose_name='Puan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Öğretmen Puanı'
        verbose_name_plural = 'Öğretmen Puanları'
        constraints = [
            models.UniqueConstraint(
                fields=['teacher', 'course_center'],
                name='unique_teacher_rating_per_center',
            ),
        ]

    def __str__(self):
        return f'{self.course_center} → {self.teacher} ({self.score})'


class TeacherFavorite(models.Model):
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Öğretmen',
    )
    course_center = models.ForeignKey(
        CourseCenter,
        on_delete=models.CASCADE,
        related_name='favorite_teachers',
        verbose_name='Kurs Merkezi',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Favori Öğretmen'
        verbose_name_plural = 'Favori Öğretmenler'
        constraints = [
            models.UniqueConstraint(
                fields=['teacher', 'course_center'],
                name='unique_teacher_favorite_per_center',
            ),
        ]

    def __str__(self):
        return f'{self.course_center} ★ {self.teacher}'


class UserSkill(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="userskills")
    skill_name = models.CharField(max_length=50, verbose_name="Yetkinlik")
    skill_degree = models.SmallIntegerField(verbose_name="Seviye")

    class Meta:
        verbose_name = "Yetkinlik"
        verbose_name_plural = "Yetkinlikler"
    
    def __str__(self):
        return self.skill_name
    
class UserEducation(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="usereducations")
    degree = models.CharField(choices=CustomUserEducationChoices.DEGREE_CHOICES, max_length=100, verbose_name="Derece")
    school_name = models.CharField(max_length=100, verbose_name="Okul/Üniversite")
    department = models.CharField(max_length=100, verbose_name="Bölüm")
    start_date = models.DateField(verbose_name="Başlangıç")
    end_date = models.DateField(null=True, blank=True, verbose_name="Bitiş")
    short_description = models.TextField(max_length=500, blank=True, default='', verbose_name="Açıklama")

    class Meta:
        verbose_name = "Eğitim"
        verbose_name_plural = "Eğitimler"
    
    def __str__(self):
        return self.school_name
    
class UserExperience(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="userexperiences")
    institution_name = models.CharField(max_length=100, verbose_name="Kurum / Kurs Merkezi Adı")
    department = models.CharField(max_length=100, verbose_name="Branş / Departman")
    start_date = models.DateField(verbose_name="Başlangıç")
    end_date = models.DateField(null=True, blank=True, verbose_name="Bitiş")
    short_description = models.TextField(max_length=500, verbose_name="Açıklama")

    class Meta:
        verbose_name = "Deneyim"
        verbose_name_plural = "Deneyimler"

    def __str__(self):
        return self.institution_name
    
class UserServices(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="userservices")
    service_name = models.CharField(max_length=50, verbose_name="Ders/Branş Adı")
    service_description = models.CharField(max_length=500, verbose_name="Açıklama")
    service_search_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Verdiği Ders"
        verbose_name_plural = "Verdiği Dersler"
    
    def __str__(self):
        return self.service_name
    
    
class UserWorks(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="userworks")
    publisher_name = models.CharField(max_length=100, verbose_name="Yayınevi Adı")
    book_name = models.CharField(max_length=100, verbose_name="Kitap Adı")
    publication_year = models.PositiveSmallIntegerField(verbose_name="Yayın Yılı")

    class Meta:
        verbose_name = "Ders Materyali"
        verbose_name_plural = "Ders Materyalleri"

    def __str__(self):
        return self.book_name
    
class UserBlogs(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="userblogs")
    blog_title = models.CharField(max_length=100, verbose_name="Blog Başlığı")
    blog_date = models.DateField(verbose_name="Tarih")
    blog_category = models.CharField(max_length=100, verbose_name="Kategori")
    blog_content = models.TextField(max_length=5000, verbose_name="İçerik")
    blog_image = models.ImageField(upload_to="images/", default="images/default.jpg", verbose_name="Görsel")
    blog_view = models.SmallIntegerField(default=0, verbose_name="Görüntülenme")

    class Meta:
        verbose_name = "Blog Yazısı"
        verbose_name_plural = "Blog Yazıları"
    
    def __str__(self):
        return self.blog_title
    
class UserAwards(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="userawards")
    award_name = models.CharField(max_length=1000, verbose_name="Sertifika/Ödül Adı")
    award_date = models.DateField(verbose_name="Tarih")

    class Meta:
        verbose_name = "Sertifika"
        verbose_name_plural = "Sertifikalar"
    
    def __str__(self):
        return self.award_name

class AdminUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return self.username