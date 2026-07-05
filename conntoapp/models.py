from django.db import models
from django.contrib.auth.models import AbstractUser
from .choices import CustomUserChoices, CustomUserEducationChoices, TeacherChoices
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=100, verbose_name="Ad Soyad")
    twitter = models.CharField(max_length=100, null=True, blank=True)
    facebook = models.CharField(max_length=100, null=True, blank=True)
    linkedin = models.CharField(max_length=100, null=True, blank=True)
    instagram = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=6, choices=CustomUserChoices.GENDER_CHOICES, verbose_name="Cinsiyet")
    birth_date = models.DateField(verbose_name="Doğum Tarihi")
    phone = models.CharField(max_length=12, null=True, blank=True, verbose_name="Telefon")
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
    city = models.CharField(max_length=30, choices=CustomUserChoices.TURKISH_CITIES, verbose_name="Şehir")
    district = models.CharField(max_length=50, null=True, blank=True, verbose_name="İlçe")
    job = models.CharField(max_length=20, blank=True, default='')
    short_description = models.CharField(max_length=100, null=True, blank=True, verbose_name="Kısa Tanıtım")
    long_description = models.TextField(max_length=500, null=True, blank=True, verbose_name="Biyografi")
    view = models.IntegerField(default=0)
    image = models.ImageField(upload_to="images/", default="images/default.jpg", null=False, blank=False)

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


class CourseCenter(models.Model):
    center_name = models.CharField(max_length=100, verbose_name="Kurs Merkezi Adı")
    center_type = models.CharField(max_length=100, verbose_name="Kurs Türü")
    teacher_capacity = models.IntegerField(verbose_name="Öğretmen Kapasitesi")
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name="E-posta")
    password = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = "Kurs Merkezi"
        verbose_name_plural = "Kurs Merkezleri"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.center_name

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
    short_description = models.TextField(max_length=500, verbose_name="Açıklama")

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
    work_title = models.CharField(max_length=100)
    work_year = models.DateField()
    work_service = models.CharField(max_length=100)
    work_name = models.CharField(max_length=100)
    work_about = models.TextField(max_length=1000)
    work_description = models.TextField(max_length=1000)
    work_image1 = models.ImageField(upload_to="images/", default="images/default.jpg")
    work_image2 = models.ImageField(upload_to="images/", default="images/default.jpg")
    work_image3 = models.ImageField(upload_to="images/", default="images/default.jpg")
    work_image4 = models.ImageField(upload_to="images/", default="images/default.jpg")
    work_image5 = models.ImageField(upload_to="images/", default="images/default.jpg")
    work_image6 = models.ImageField(upload_to="images/", default="images/default.jpg")
    
    def __str__(self):
        return self.work_name
    
class UserBlogs(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="userblogs")
    blog_title = models.CharField(max_length=100)
    blog_date = models.DateField()
    blog_category = models.CharField(max_length=100)
    blog_content = models.TextField(max_length=5000)
    blog_image = models.ImageField(upload_to="images/", default="images/default.jpg")
    blog_view = models.SmallIntegerField(default=0)
    
    def __str__(self):
        return self.blog_title
    
class UserAwards(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="userawards")
    award_name = models.CharField(max_length=30, verbose_name="Sertifika/Ödül Adı")
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