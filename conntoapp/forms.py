from django import forms
from datetime import date
from .models import (
    CustomUser, UserSkill, UserEducation, UserExperience,
    UserServices, UserWorks, UserBlogs, UserAwards, CourseCenter, AdminUser,
)
from .choices import CustomUserChoices, CustomUserEducationChoices, TeacherChoices
from .district_data import get_district_choices, is_valid_district
from django.contrib.auth.forms import PasswordChangeForm


def calendar_date_widget(required=True):
    attrs = {
        'type': 'date',
        'class': 'connto-date-picker',
        'title': 'Takvimden tarih seçin',
    }
    if required:
        attrs['required'] = True
    return forms.DateInput(format='%Y-%m-%d', attrs=attrs)


def configure_calendar_date_field(field, *, max_date=None, min_date=None, required=None):
    field.input_formats = ['%Y-%m-%d']
    field.widget.format = '%Y-%m-%d'
    field.widget.attrs.setdefault('type', 'date')
    css_class = field.widget.attrs.get('class', '')
    if 'connto-date-picker' not in css_class.split():
        field.widget.attrs['class'] = f'{css_class} connto-date-picker'.strip()
    field.widget.attrs.setdefault('title', 'Takvimden tarih seçin')
    if max_date is not None:
        field.widget.attrs['max'] = max_date.isoformat()
    if min_date is not None:
        field.widget.attrs['min'] = min_date.isoformat()
    if required is False:
        field.widget.attrs.pop('required', None)
    elif required is True:
        field.widget.attrs['required'] = True


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
            'birth_date': calendar_date_widget(required=True),
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
        today = date.today()
        configure_calendar_date_field(
            self.fields['birth_date'],
            max_date=today,
            min_date=date(today.year - 100, 1, 1),
            required=True,
        )
        self.fields['birth_date'].widget.attrs['autocomplete'] = 'bday'
        self.fields['birth_date'].widget.attrs['title'] = 'Takvimden doğum tarihi seçin'


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
    skill_degree = forms.IntegerField(
        min_value=0,
        max_value=100,
        label='Seviye',
        error_messages={
            'min_value': 'Yetkinlik seviyesi 0 ile 100 arasında olmalıdır.',
            'max_value': 'Yetkinlik seviyesi 0 ile 100 arasında olmalıdır.',
            'invalid': 'Geçerli bir sayı girin.',
            'required': 'Yetkinlik seviyesi zorunludur.',
        },
        widget=forms.NumberInput(attrs={
            'type': 'number',
            'min': 0,
            'max': 100,
            'step': 1,
            'required': True,
            'placeholder': '0-100',
            'class': 'skill-degree-input',
        }),
    )

    class Meta:
        model = UserSkill
        fields = ['skill_name', 'skill_degree']
        widgets = {
            'skill_name': forms.TextInput(attrs={'required': True, 'placeholder': 'Yetkinlik adı'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if not self.user and self.instance.pk:
            self.user = self.instance.custom_user

    def clean_skill_name(self):
        skill_name = self.cleaned_data.get('skill_name', '').strip()
        if not skill_name:
            raise forms.ValidationError('Yetkinlik adı zorunludur.')
        return skill_name

    def clean_skill_degree(self):
        degree = self.cleaned_data.get('skill_degree')
        if degree is not None and (degree < 0 or degree > 100):
            raise forms.ValidationError('Yetkinlik seviyesi 0 ile 100 arasında olmalıdır.')
        return degree

    def clean(self):
        cleaned_data = super().clean()
        skill_name = cleaned_data.get('skill_name')
        if not skill_name or not self.user:
            return cleaned_data

        duplicates = UserSkill.objects.filter(
            custom_user=self.user,
            skill_name__iexact=skill_name,
        )
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if duplicates.exists():
            self.add_error(
                'skill_name',
                'Bu yetkinlik daha önce kaydedildi. Aynı yetkinliği tekrar ekleyemezsiniz.',
            )

        return cleaned_data


class TeacherEducationForm(forms.ModelForm):
    is_ongoing = forms.BooleanField(
        required=False,
        label='',
        widget=forms.CheckboxInput(attrs={'class': 'edu-ongoing-checkbox'}),
    )

    class Meta:
        model = UserEducation
        fields = ['school_name', 'department', 'degree', 'start_date', 'end_date', 'short_description']
        widgets = {
            'school_name': forms.TextInput(attrs={'required': True}),
            'department': forms.TextInput(attrs={'required': True}),
            'degree': forms.Select(
                choices=[('', 'Seçiniz'), *CustomUserEducationChoices.DEGREE_CHOICES],
                attrs={'required': True},
            ),
            'start_date': calendar_date_widget(required=True),
            'end_date': calendar_date_widget(required=False),
            'short_description': forms.Textarea(attrs={'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = date.today()
        configure_calendar_date_field(self.fields['start_date'], max_date=today, required=True)
        configure_calendar_date_field(self.fields['end_date'], max_date=today, required=False)
        if self.instance.pk and not self.instance.end_date:
            self.fields['is_ongoing'].initial = True

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('is_ongoing'):
            cleaned_data['end_date'] = None
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('is_ongoing'):
            instance.end_date = None
        if commit:
            instance.save()
        return instance


class TeacherExperienceForm(forms.ModelForm):
    class Meta:
        model = UserExperience
        fields = ['institution_name', 'department', 'start_date', 'end_date', 'short_description']
        widgets = {
            'institution_name': forms.TextInput(attrs={'required': True, 'placeholder': 'Kurum / Kurs Merkezi Adı'}),
            'department': forms.TextInput(attrs={'required': True, 'placeholder': 'Branş / Departman'}),
            'start_date': calendar_date_widget(required=True),
            'end_date': calendar_date_widget(required=False),
            'short_description': forms.Textarea(attrs={'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = date.today()
        configure_calendar_date_field(self.fields['start_date'], max_date=today, required=True)
        configure_calendar_date_field(self.fields['end_date'], max_date=today, required=False)


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
            'work_year': calendar_date_widget(required=True),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configure_calendar_date_field(self.fields['work_year'], max_date=date.today(), required=True)


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
            'award_name': forms.TextInput(attrs={
                'required': True,
                'placeholder': 'Sertifika/Ödül adı',
                'maxlength': 1000,
            }),
            'award_date': calendar_date_widget(required=True),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configure_calendar_date_field(self.fields['award_date'], max_date=date.today(), required=True)


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
