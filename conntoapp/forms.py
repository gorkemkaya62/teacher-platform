from django import forms
from datetime import date
from .models import (
    CustomUser, UserSkill, UserEducation, UserExperience,
    UserServices, UserWorks, UserAwards, CourseCenter, AdminUser,
)
from .choices import CustomUserChoices, CustomUserEducationChoices, TeacherChoices
from .district_data import get_district_choices, is_valid_district
from .image_utils import normalize_profile_image
from .phone_data import (
    COUNTRY_DIAL_CODE_CHOICES,
    DEFAULT_COUNTRY_CODE,
    format_international_phone,
    split_international_phone,
    validate_national_number,
)
from .social_links import SOCIAL_LINK_RULES, validate_optional_social_link
from .widgets import PhoneCountryCodeWidget
from django.contrib.auth.forms import PasswordChangeForm


def work_schedule_to_flags(work_schedule):
    return {
        'works_full_time': work_schedule in ('tam_zamanli', 'her_ikisi'),
        'works_part_time': work_schedule in ('yari_zamanli', 'her_ikisi'),
    }


def flags_to_work_schedule(works_full_time, works_part_time):
    if works_full_time and works_part_time:
        return 'her_ikisi'
    if works_full_time:
        return 'tam_zamanli'
    if works_part_time:
        return 'yari_zamanli'
    return ''


class SocialLinksFormMixin:
    def _inject_social_platform_fields(self):
        for field_name, rules in SOCIAL_LINK_RULES.items():
            enable_name = f'enable_social_{field_name}'
            initial = False
            if self.data:
                initial = enable_name in self.data
            elif getattr(self, 'instance', None) and getattr(self.instance, 'pk', None):
                existing = getattr(self.instance, field_name, None) or ''
                initial = bool(str(existing).strip())

            self.fields[enable_name] = forms.BooleanField(
                required=False,
                label=rules['label'],
                initial=initial,
                widget=forms.CheckboxInput(attrs={
                    'class': 'connto-social-platform-checkbox',
                    'data-social-platform': field_name,
                }),
            )

    def _configure_social_link_fields(self):
        for field_name, rules in SOCIAL_LINK_RULES.items():
            if field_name not in self.fields:
                continue
            field = self.fields[field_name]
            field.required = False
            css_class = field.widget.attrs.get('class', '')
            field.widget.attrs.update({
                'class': f'{css_class} connto-social-link-input'.strip(),
                'data-social-prefix': rules['prefix'].rstrip('/'),
                'data-social-label': rules['label'],
                'data-social-platform': field_name,
                'placeholder': rules['placeholder'],
            })

    def _clean_social_links(self, cleaned_data):
        for field_name, rules in SOCIAL_LINK_RULES.items():
            enable_name = f'enable_social_{field_name}'
            enabled = cleaned_data.get(enable_name, False)
            if not enabled:
                cleaned_data[field_name] = ''
                continue
            if field_name in self.errors:
                continue
            try:
                cleaned_data[field_name] = validate_optional_social_link(
                    cleaned_data.get(field_name),
                    prefix=rules['prefix'],
                    label=rules['label'],
                )
            except forms.ValidationError as exc:
                self.add_error(field_name, exc)
        return cleaned_data


class WorkScheduleCheckboxMixin:
    def _inject_work_schedule_fields(self):
        self.fields['works_full_time'] = forms.BooleanField(
            required=False,
            label='Tam Zamanlı',
        )
        self.fields['works_part_time'] = forms.BooleanField(
            required=False,
            label='Yarı Zamanlı',
        )
        self._init_work_schedule_checkboxes()

    def _init_work_schedule_checkboxes(self):
        if getattr(self, 'instance', None) and getattr(self.instance, 'pk', None):
            flags = work_schedule_to_flags(self.instance.work_schedule)
            self.fields['works_full_time'].initial = flags['works_full_time']
            self.fields['works_part_time'].initial = flags['works_part_time']

    def _clean_work_schedule_checkboxes(self, cleaned_data):
        works_full_time = cleaned_data.get('works_full_time')
        works_part_time = cleaned_data.get('works_part_time')
        if not works_full_time and not works_part_time:
            self.add_error('works_full_time', 'required')
            return cleaned_data
        cleaned_data['work_schedule'] = flags_to_work_schedule(
            works_full_time,
            works_part_time,
        )
        return cleaned_data

    def _apply_work_schedule_to_instance(self, instance):
        instance.work_schedule = self.cleaned_data['work_schedule']
        return instance


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


def latest_birth_date_for_minimum_age(min_age=18):
    today = date.today()
    year = today.year - min_age
    try:
        return date(year, today.month, today.day)
    except ValueError:
        return date(year, today.month, 28)


def is_at_least_age(birth_date, min_age=18):
    return birth_date <= latest_birth_date_for_minimum_age(min_age)


class CityDistrictFormMixin:
    def _selected_city(self):
        if self.data.get("city"):
            return self.data.get("city")
        if self.instance and getattr(self.instance, "pk", None):
            return self.instance.city
        return None

    def _configure_district_field(self):
        city = self._selected_city()
        initial_district = ""
        if self.data.get("district"):
            initial_district = self.data.get("district")
        elif self.instance and getattr(self.instance, "pk", None) and self.instance.district:
            initial_district = self.instance.district

        district_attrs = {
            "required": True,
            "id": "id_district",
            "class": "browser-default city-district-select",
            "data-selected-district": initial_district,
        }
        if not city:
            district_attrs["disabled"] = "disabled"

        self.fields["district"] = forms.ChoiceField(
            choices=get_district_choices(city),
            required=True,
            label="İlçe",
            widget=forms.Select(attrs=district_attrs),
        )
        if initial_district:
            self.fields["district"].initial = initial_district

    def clean(self):
        cleaned_data = super().clean()
        city = cleaned_data.get("city")
        district = cleaned_data.get("district")
        if city and district and not is_valid_district(city, district):
            self.add_error("district", "Seçilen ilçe bu şehre ait değil.")
        return cleaned_data


class PhoneNumberFormMixin:
    def _inject_phone_fields(self, *, required=True):
        self.fields['phone_country_code'] = forms.ChoiceField(
            choices=COUNTRY_DIAL_CODE_CHOICES,
            initial=DEFAULT_COUNTRY_CODE,
            label='Ülke Kodu',
            widget=PhoneCountryCodeWidget(attrs={
                'class': 'connto-phone-code-native browser-default',
                'aria-label': 'Ülke kodu',
            }),
        )
        self.fields['phone_number'] = forms.CharField(
            label='Telefon',
            max_length=15,
            widget=forms.TextInput(attrs={
                'type': 'tel',
                'inputmode': 'numeric',
                'autocomplete': 'tel-national',
                'class': 'connto-phone-number',
                'placeholder': '5XX XXX XX XX',
                'pattern': '[1-9][0-9]*',
                'title': 'Telefon numarasını başında 0 olmadan girin',
            }),
        )
        self._configure_phone_fields(required=required)

    def _configure_phone_fields(self, *, required=True, stored_phone=None):
        if stored_phone is None:
            if getattr(self.instance, 'pk', None):
                stored_phone = getattr(self.instance, 'phone', None)
            elif self.initial.get('phone'):
                stored_phone = self.initial.get('phone')

        code, number = split_international_phone(stored_phone)
        self.fields['phone_country_code'].initial = code
        self.fields['phone_number'].initial = number
        self.fields['phone_country_code'].label = ''
        self._phone_required = required

        if required:
            self.fields['phone_number'].required = True
            self.fields['phone_country_code'].required = True
            self.fields['phone_number'].widget.attrs['required'] = True
            self.fields['phone_country_code'].widget.attrs['required'] = True
        else:
            self.fields['phone_number'].required = False
            self.fields['phone_number'].widget.attrs.pop('required', None)

    def clean_phone_number(self):
        value = self.cleaned_data.get('phone_number', '')
        required = getattr(self, '_phone_required', True)
        try:
            return validate_national_number(value, required=required)
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc

    def get_formatted_phone(self):
        national_number = self.cleaned_data.get('phone_number', '')
        if not national_number:
            return ''
        return format_international_phone(
            self.cleaned_data.get('phone_country_code'),
            national_number,
        )


# Öğretmen Kayıt / Giriş Formları

class TeacherRegisterForm(WorkScheduleCheckboxMixin, PhoneNumberFormMixin, CityDistrictFormMixin, forms.ModelForm):
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
        self._inject_phone_fields(required=True)
        today = date.today()
        configure_calendar_date_field(
            self.fields['birth_date'],
            max_date=today,
            min_date=date(today.year - 100, 1, 1),
            required=True,
        )
        self.fields['birth_date'].widget.attrs['autocomplete'] = 'bday'
        self.fields['birth_date'].widget.attrs['title'] = 'Kayıt için en az 18 yaşında olmalısınız'
        self.fields['birth_date'].widget.attrs['data-register-min-age'] = '18'
        self.fields['fullname'].label = 'Ad Soyad'
        self.fields['password'].label = 'Şifre'
        self.fields['email'].label = 'E-posta'
        self.fields['gender'].label = 'Cinsiyet'
        self.fields['birth_date'].label = 'Doğum Tarihi'
        self.fields['branch'].label = 'Branş'
        self.fields['city'].label = 'Şehir'
        self._inject_work_schedule_fields()

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and not is_at_least_age(birth_date, 18):
            raise forms.ValidationError('Kayıt olmak için en az 18 yaşında olmalısınız.')
        return birth_date

    def clean(self):
        cleaned_data = super().clean()
        return self._clean_work_schedule_checkboxes(cleaned_data)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = self.get_formatted_phone()
        self._apply_work_schedule_to_instance(user)
        if commit:
            user.save()
        return user


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

class TeacherProfileForm(
    SocialLinksFormMixin,
    WorkScheduleCheckboxMixin,
    PhoneNumberFormMixin,
    CityDistrictFormMixin,
    forms.ModelForm,
):
    class Meta:
        model = CustomUser
        fields = [
            "branch", "experience_years", "city", "district", "gender",
            "twitter", "instagram", "linkedin", "facebook",
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
            'image': forms.FileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configure_district_field()
        self._inject_phone_fields(required=False)
        self._inject_work_schedule_fields()
        self._inject_social_platform_fields()
        self._configure_social_link_fields()

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data = self._clean_work_schedule_checkboxes(cleaned_data)
        return self._clean_social_links(cleaned_data)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = self.get_formatted_phone() or None
        self._apply_work_schedule_to_instance(user)
        image = self.files.get('image')
        if image is not None:
            user.image = normalize_profile_image(image)
        if commit:
            user.save()
        return user


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
            'short_description': forms.Textarea(attrs={'placeholder': 'İsteğe bağlı'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['short_description'].required = False
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
    is_ongoing = forms.BooleanField(
        required=False,
        label='',
        widget=forms.CheckboxInput(attrs={'class': 'edu-ongoing-checkbox'}),
    )

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


class TeacherServiceForm(forms.ModelForm):
    class Meta:
        model = UserServices
        fields = ['service_name', 'service_description']
        widgets = {
            'service_name': forms.TextInput(attrs={'required': True, 'placeholder': 'Ders/Branş adı'}),
            'service_description': forms.Textarea(attrs={'required': True}),
        }


class TeacherWorkForm(forms.ModelForm):
    publication_year = forms.TypedChoiceField(
        label='Yayın Yılı',
        choices=[],
        coerce=int,
        empty_value=None,
        widget=forms.Select(attrs={
            'required': True,
            'class': 'browser-default connto-panel-select',
        }),
    )

    class Meta:
        model = UserWorks
        fields = ['publisher_name', 'book_name', 'publication_year']
        widgets = {
            'publisher_name': forms.TextInput(attrs={
                'required': True,
                'placeholder': 'Yayınevi adı',
            }),
            'book_name': forms.TextInput(attrs={
                'required': True,
                'placeholder': 'Kitap adı',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_year = date.today().year
        self.fields['publication_year'].choices = [
            ('', 'Seçiniz'),
            *[(str(year), str(year)) for year in range(current_year, current_year - 100, -1)],
        ]
        if self.instance.pk and self.instance.publication_year:
            self.fields['publication_year'].initial = str(self.instance.publication_year)

    def clean_publication_year(self):
        value = self.cleaned_data.get('publication_year')
        if value in (None, ''):
            raise forms.ValidationError('Yayın yılı seçiniz.')
        return int(value)


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Mevcut Şifre'
        self.fields['new_password1'].label = 'Yeni Şifre'
        self.fields['new_password2'].label = 'Yeni Şifre (Tekrar)'


class AdminLoginForm(forms.Form):
    username = forms.CharField(
        label='Kullanıcı Adı',
        widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Kullanıcı adınızı girin',
    }))
    password = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Şifrenizi girin',
    }))
