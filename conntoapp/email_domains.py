import re

from django import forms
from django.core.validators import validate_email

EMAIL_DOMAIN_CHOICES = [
    ('gmail.com', 'gmail.com'),
    ('hotmail.com', 'hotmail.com'),
    ('outlook.com', 'outlook.com'),
    ('yahoo.com', 'yahoo.com'),
    ('icloud.com', 'icloud.com'),
    ('yandex.com', 'yandex.com'),
    ('live.com', 'live.com'),
    ('msn.com', 'msn.com'),
    ('custom', 'Diğer'),
]

EMAIL_LOCAL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+$')


def split_email_address(value):
    if not value or '@' not in str(value):
        return '', 'gmail.com', ''

    local, domain = str(value).rsplit('@', 1)
    domain = domain.lower().strip()
    known_domains = {choice[0] for choice in EMAIL_DOMAIN_CHOICES if choice[0] != 'custom'}
    if domain in known_domains:
        return local.strip(), domain, ''
    return local.strip(), 'custom', domain


def combine_email_address(local, domain, custom_domain=''):
    local_part = (local or '').strip().lower()
    if not local_part:
        raise forms.ValidationError('E-posta adresinin kullanıcı adı kısmını girin.')

    if not EMAIL_LOCAL_PATTERN.match(local_part):
        raise forms.ValidationError('Geçerli bir e-posta kullanıcı adı girin.')

    if domain == 'custom':
        domain_part = (custom_domain or '').strip().lower().lstrip('@')
        if not domain_part or '.' not in domain_part:
            raise forms.ValidationError('Geçerli bir e-posta uzantısı girin.')
    else:
        domain_part = (domain or '').strip().lower().lstrip('@')
        if not domain_part:
            raise forms.ValidationError('E-posta uzantısı seçin.')

    email = f'{local_part}@{domain_part}'
    try:
        validate_email(email)
    except forms.ValidationError as exc:
        raise forms.ValidationError('Geçerli bir e-posta adresi girin.') from exc
    return email


class EmailDomainFormMixin:
    email_domain_field_label = 'E-posta'

    def _inject_email_domain_fields(self, *, required=True, after='password'):
        initial_local = ''
        initial_domain = 'gmail.com'
        initial_custom = ''

        if self.data:
            initial_local = self.data.get('email_local', '')
            initial_domain = self.data.get('email_domain', 'gmail.com')
            initial_custom = self.data.get('email_domain_custom', '')
        else:
            existing_email = self.initial.get('email')
            if not existing_email and getattr(self, 'instance', None):
                existing_email = getattr(self.instance, 'email', None)
            if existing_email:
                initial_local, initial_domain, initial_custom = split_email_address(existing_email)

        self.fields['email_local'] = forms.CharField(
            required=required,
            label=self.email_domain_field_label,
            initial=initial_local,
            widget=forms.TextInput(attrs={
                'type': 'text',
                'required': required,
                'placeholder': 'kullaniciadi',
                'class': 'connto-email-local-input',
                'autocomplete': 'username',
            }),
        )
        self.fields['email_domain'] = forms.ChoiceField(
            required=required,
            label='E-posta Uzantısı',
            choices=EMAIL_DOMAIN_CHOICES,
            initial=initial_domain,
            widget=forms.Select(attrs={
                'required': required,
                'class': 'browser-default connto-email-domain-select',
            }),
        )
        self.fields['email_domain_custom'] = forms.CharField(
            required=False,
            label='Özel E-posta Uzantısı',
            initial=initial_custom,
            widget=forms.TextInput(attrs={
                'type': 'text',
                'placeholder': 'ornek.com',
                'class': 'connto-email-domain-custom-input',
            }),
        )

        if 'email' in self.fields:
            del self.fields['email']

        if after in self.fields:
            ordered_keys = [name for name in self.fields if name not in {'email_local', 'email_domain', 'email_domain_custom'}]
            insert_at = ordered_keys.index(after) + 1
            for offset, field_name in enumerate(['email_local', 'email_domain', 'email_domain_custom']):
                ordered_keys.insert(insert_at + offset, field_name)
            self.order_fields(ordered_keys)

    def _clean_email_from_parts(self, cleaned_data):
        if any(field in self.errors for field in ('email_local', 'email_domain', 'email_domain_custom')):
            return cleaned_data

        try:
            cleaned_data['email'] = combine_email_address(
                cleaned_data.get('email_local'),
                cleaned_data.get('email_domain'),
                cleaned_data.get('email_domain_custom'),
            )
        except forms.ValidationError as exc:
            self.add_error('email_local', exc)
        return cleaned_data
