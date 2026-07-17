from urllib.parse import urlparse

from django import forms

SOCIAL_LINK_RULES = {
    'twitter': {
        'prefix': 'https://x.com/',
        'label': 'X',
        'placeholder': 'https://x.com/kullaniciadi',
    },
    'instagram': {
        'prefix': 'https://www.instagram.com/',
        'label': 'Instagram',
        'placeholder': 'https://www.instagram.com/kullaniciadi',
    },
    'linkedin': {
        'prefix': 'https://www.linkedin.com/',
        'label': 'LinkedIn',
        'placeholder': 'https://www.linkedin.com/in/kullaniciadi',
    },
    'facebook': {
        'prefix': 'https://www.facebook.com/',
        'label': 'Facebook',
        'placeholder': 'https://www.facebook.com/kullaniciadi',
    },
}


def validate_optional_social_link(value, *, prefix, label):
    if value is None or not str(value).strip():
        return ''

    normalized = str(value).strip()
    if not normalized.lower().startswith(prefix.lower()):
        raise forms.ValidationError(
            f'{label} için yalnızca {prefix.rstrip("/")} ile başlayan bağlantılar kullanılabilir.'
        )

    parsed = urlparse(normalized)
    if parsed.scheme != 'https':
        raise forms.ValidationError(f'{label} bağlantısı https ile başlamalıdır.')

    if not (parsed.path or '').strip('/'):
        raise forms.ValidationError(f'{label} için geçerli bir profil bağlantısı girin.')

    return normalized
