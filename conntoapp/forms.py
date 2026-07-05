from django import forms
from .models import (
    CustomUser, UserSkill, UserEducation, UserExperience,
    UserServices, UserWorks, UserBlogs, UserAwards, CourseCenter, AdminUser,
)
from .choices import CustomUserChoices, CustomUserEducationChoices, TeacherChoices
from .district_data import get_district_choices, is_valid_district
from django.contrib.auth.forms import PasswordChangeForm


class CityDistrictFormMixin:
    def _selected_city(self):
        if self.data.get("city"):
            return self.data.get("city")
        if self.instance and getattr(self.instance, "pk", None):
            return self.instance.city
        return None

    def _configure_district_field(self):
        self.fields["district"] = forms.ChoiceField(
            choices=get_district_choices(self._selected_city()),
            required=True,
            label="İlçe",
            widget=forms.Select(attrs={
                "required": True,
                "id": "id_district",
                "class": "browser-default city-district-select",
            }),
        )
        if self.instance and getattr(self.instance, "pk", None) and self.instance.district:
            self.fields["district"].initial = self.instance.district

    def clean(self):
        cleaned_data = super().clean()
        city = cleaned_data.get("city")
        district = cleaned_data.get("district")
        if city and district and not is_valid_district(city, district):
            self.add_error("district", "Seçilen ilçe bu şehre ait değil.")
        return cleaned_data


# Öğretmen Kayıt / Giriş Formları

class TeacherRegisterForm(CityDistrictFormMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["fullname", "password", "email", "gender", "birth_date", "branch", "city", "district"]

        widgets = {
            'fullname': forms.TextInput(attrs={'type': 'text', 'required': True, 'placeholder': 'Ad Soyad'}),
            'password': forms.PasswordInput(attrs={'type': 'password', 'required': True, 'placeholder': 'Şifre'}),
            'email': forms.EmailInput(attrs={'type': 'email', 'required': True, 'placeholder': 'E-posta'}),
            'gender': forms.Select(choices=CustomUserChoices.GENDER_CHOICES, attrs={'required': True}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'branch': forms.Select(choices=TeacherChoices.BRANCH_CHOICES, attrs={'required': True}),
            'city': forms.Select(choices=CustomUserChoices.TURKISH_CITIES, attrs={
                'required': True,
                'id': 'id_city',
                'class': 'browser-default city-district-select',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configure_district_field()


class CourseCenterRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'type': 'password',
        'required': True,
        'placeholder': 'Şifre',
    }))

    class Meta:
        model = CourseCenter
        fields = ['center_name', 'center_type', 'teacher_capacity', 'email', 'password']

        widgets = {
            'center_name': forms.TextInput(attrs={
                'type': 'text', 'required': True, 'placeholder': 'Kurs Merkezi Adı',
            }),
            'center_type': forms.TextInput(attrs={
                'type': 'text', 'required': True,
                'placeholder': 'Kurs Türü (örn: Dil Kursu, Sınav Hazırlık)',
            }),
            'teacher_capacity': forms.NumberInput(attrs={
                'type': 'number', 'required': True, 'placeholder': 'Öğretmen Kapasitesi',
            }),
            'email': forms.EmailInput(attrs={
                'type': 'email', 'required': True, 'placeholder': 'Kurs Merkezi E-posta',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CourseCenter.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten kullanılıyor.")
        return email

    def save(self, commit=True):
        course_center = super().save(commit=False)
        course_center.set_password(self.cleaned_data["password"])
        if commit:
            course_center.save()
        return course_center


class TeacherLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'type': 'email', 'required': True, 'placeholder': 'E-posta',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'type': 'password', 'required': True, 'placeholder': 'Şifre',
    }))
    is_course_center = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'filled-in',
        'id': 'is_course_center_login',
    }))


# Öğretmen Profil Formları

class TeacherProfileForm(CityDistrictFormMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "branch", "experience_years", "city", "district", "gender",
            "twitter", "instagram", "linkedin", "facebook", "phone",
            "short_description", "long_description", "image",
        ]
        widgets = {
            'branch': forms.Select(choices=TeacherChoices.BRANCH_CHOICES, attrs={'required': True}),
            'experience_years': forms.Select(choices=TeacherChoices.EXPERIENCE_CHOICES, attrs={'required': True}),
            'city': forms.Select(choices=CustomUserChoices.TURKISH_CITIES, attrs={
                'required': True,
                'id': 'id_city',
                'class': 'browser-default city-district-select',
            }),
            'gender': forms.Select(choices=CustomUserChoices.GENDER_CHOICES, attrs={'required': True}),
            'twitter': forms.TextInput(attrs={'required': False}),
            'instagram': forms.TextInput(attrs={'required': False}),
            'linkedin': forms.TextInput(attrs={'required': False}),
            'facebook': forms.TextInput(attrs={'required': False}),
            'short_description': forms.TextInput(attrs={'required': True, 'placeholder': 'Kısa tanıtım'}),
            'long_description': forms.Textarea(attrs={'required': True, 'placeholder': 'Biyografi ve eğitim özeti'}),
            'phone': forms.NumberInput(attrs={'type': 'number'}),
            'image': forms.FileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configure_district_field()


class TeacherSkillForm(forms.ModelForm):
    class Meta:
        model = UserSkill
        fields = ['skill_name', 'skill_degree']
        widgets = {
            'skill_name': forms.TextInput(attrs={'required': True, 'placeholder': 'Yetkinlik adı'}),
            'skill_degree': forms.NumberInput(attrs={'type': 'number', 'placeholder': '0-100'}),
        }


class TeacherEducationForm(forms.ModelForm):
    class Meta:
        model = UserEducation
        fields = ['school_name', 'department', 'degree', 'start_date', 'end_date', 'short_description']
        widgets = {
            'school_name': forms.TextInput(attrs={'required': True}),
            'department': forms.TextInput(attrs={'required': True}),
            'degree': forms.Select(choices=CustomUserEducationChoices.DEGREE_CHOICES, attrs={'required': True}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'required': False}),
            'short_description': forms.Textarea(attrs={'required': True}),
        }


class TeacherExperienceForm(forms.ModelForm):
    class Meta:
        model = UserExperience
        fields = ['institution_name', 'department', 'start_date', 'end_date', 'short_description']
        widgets = {
            'institution_name': forms.TextInput(attrs={'required': True, 'placeholder': 'Kurum / Kurs Merkezi Adı'}),
            'department': forms.TextInput(attrs={'required': True, 'placeholder': 'Branş / Departman'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'required': False}),
            'short_description': forms.Textarea(attrs={'required': True}),
        }


class TeacherServiceForm(forms.ModelForm):
    class Meta:
        model = UserServices
        fields = ['service_name', 'service_description']
        widgets = {
            'service_name': forms.TextInput(attrs={'required': True, 'placeholder': 'Ders/Branş adı'}),
            'service_description': forms.Textarea(attrs={'required': True}),
        }


class TeacherWorkForm(forms.ModelForm):
    class Meta:
        model = UserWorks
        fields = [
            'work_title', 'work_year', 'work_service', 'work_name',
            'work_about', 'work_description',
            'work_image1', 'work_image2', 'work_image3',
            'work_image4', 'work_image5', 'work_image6',
        ]
        widgets = {
            'work_title': forms.TextInput(attrs={'required': True}),
            'work_year': forms.DateInput(attrs={'required': True, 'type': 'date'}),
            'work_service': forms.TextInput(attrs={'required': True}),
            'work_name': forms.TextInput(attrs={'required': True}),
            'work_about': forms.Textarea(attrs={'required': True}),
            'work_description': forms.Textarea(attrs={'required': True}),
            'work_image1': forms.FileInput(attrs={'required': True, 'accept': 'image/*'}),
            'work_image2': forms.FileInput(attrs={'required': True, 'accept': 'image/*'}),
            'work_image3': forms.FileInput(attrs={'required': True, 'accept': 'image/*'}),
            'work_image4': forms.FileInput(attrs={'required': True, 'accept': 'image/*'}),
            'work_image5': forms.FileInput(attrs={'required': True, 'accept': 'image/*'}),
            'work_image6': forms.FileInput(attrs={'required': True, 'accept': 'image/*'}),
        }


class TeacherBlogForm(forms.ModelForm):
    class Meta:
        model = UserBlogs
        fields = ['blog_title', 'blog_category', 'blog_content', 'blog_image']
        widgets = {
            'blog_title': forms.TextInput(attrs={'required': True}),
            'blog_category': forms.TextInput(attrs={'required': True}),
            'blog_content': forms.Textarea(attrs={'required': True}),
            'blog_image': forms.FileInput(attrs={'required': True, 'accept': 'image/*'}),
        }


class TeacherCertificateForm(forms.ModelForm):
    class Meta:
        model = UserAwards
        fields = ['award_name', 'award_date']
        widgets = {
            'award_name': forms.TextInput(attrs={'required': True, 'placeholder': 'Sertifika/Ödül adı'}),
            'award_date': forms.DateInput(attrs={'type': 'date', 'required': True}),
        }


class TeacherPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']
        widgets = {
            'old_password': forms.PasswordInput(attrs={'type': 'password', 'required': True}),
            'new_password1': forms.PasswordInput(attrs={'type': 'password', 'required': True}),
            'new_password2': forms.PasswordInput(attrs={'type': 'password', 'required': True}),
        }


class AdminLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Kullanıcı adınızı girin',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Şifrenizi girin',
    }))
