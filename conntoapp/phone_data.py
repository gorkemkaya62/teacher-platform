import re

DEFAULT_COUNTRY_CODE = '+90'


def flag_emoji(iso_code):
    return ''.join(chr(ord(char) + 127397) for char in iso_code.upper())


def dial_code_label(code, iso_code):
    return f'{flag_emoji(iso_code)} {code}'


# (ülke kodu, ISO 3166-1 alpha-2) — Türkiye varsayılan, sonra alfabetik ülke sırası.
COUNTRY_DIAL_CODES = [
    (DEFAULT_COUNTRY_CODE, 'TR'),
    ('+93', 'AF'),
    ('+355', 'AL'),
    ('+213', 'DZ'),
    ('+376', 'AD'),
    ('+244', 'AO'),
    ('+54', 'AR'),
    ('+374', 'AM'),
    ('+61', 'AU'),
    ('+43', 'AT'),
    ('+994', 'AZ'),
    ('+973', 'BH'),
    ('+880', 'BD'),
    ('+32', 'BE'),
    ('+501', 'BZ'),
    ('+229', 'BJ'),
    ('+975', 'BT'),
    ('+591', 'BO'),
    ('+387', 'BA'),
    ('+267', 'BW'),
    ('+55', 'BR'),
    ('+673', 'BN'),
    ('+359', 'BG'),
    ('+226', 'BF'),
    ('+257', 'BI'),
    ('+855', 'KH'),
    ('+237', 'CM'),
    ('+1', 'US'),
    ('+238', 'CV'),
    ('+236', 'CF'),
    ('+235', 'TD'),
    ('+56', 'CL'),
    ('+86', 'CN'),
    ('+57', 'CO'),
    ('+269', 'KM'),
    ('+242', 'CG'),
    ('+243', 'CD'),
    ('+506', 'CR'),
    ('+385', 'HR'),
    ('+53', 'CU'),
    ('+357', 'CY'),
    ('+420', 'CZ'),
    ('+45', 'DK'),
    ('+253', 'DJ'),
    ('+593', 'EC'),
    ('+20', 'EG'),
    ('+503', 'SV'),
    ('+372', 'EE'),
    ('+251', 'ET'),
    ('+358', 'FI'),
    ('+33', 'FR'),
    ('+995', 'GE'),
    ('+49', 'DE'),
    ('+233', 'GH'),
    ('+30', 'GR'),
    ('+502', 'GT'),
    ('+224', 'GN'),
    ('+509', 'HT'),
    ('+504', 'HN'),
    ('+852', 'HK'),
    ('+36', 'HU'),
    ('+354', 'IS'),
    ('+91', 'IN'),
    ('+62', 'ID'),
    ('+98', 'IR'),
    ('+964', 'IQ'),
    ('+353', 'IE'),
    ('+972', 'IL'),
    ('+39', 'IT'),
    ('+81', 'JP'),
    ('+962', 'JO'),
    ('+7', 'KZ'),
    ('+254', 'KE'),
    ('+965', 'KW'),
    ('+996', 'KG'),
    ('+856', 'LA'),
    ('+371', 'LV'),
    ('+961', 'LB'),
    ('+370', 'LT'),
    ('+352', 'LU'),
    ('+853', 'MO'),
    ('+389', 'MK'),
    ('+261', 'MG'),
    ('+60', 'MY'),
    ('+960', 'MV'),
    ('+223', 'ML'),
    ('+356', 'MT'),
    ('+52', 'MX'),
    ('+373', 'MD'),
    ('+377', 'MC'),
    ('+976', 'MN'),
    ('+382', 'ME'),
    ('+212', 'MA'),
    ('+258', 'MZ'),
    ('+95', 'MM'),
    ('+977', 'NP'),
    ('+31', 'NL'),
    ('+64', 'NZ'),
    ('+505', 'NI'),
    ('+234', 'NG'),
    ('+47', 'NO'),
    ('+968', 'OM'),
    ('+92', 'PK'),
    ('+970', 'PS'),
    ('+507', 'PA'),
    ('+595', 'PY'),
    ('+51', 'PE'),
    ('+63', 'PH'),
    ('+48', 'PL'),
    ('+351', 'PT'),
    ('+974', 'QA'),
    ('+40', 'RO'),
    ('+966', 'SA'),
    ('+381', 'RS'),
    ('+65', 'SG'),
    ('+421', 'SK'),
    ('+386', 'SI'),
    ('+27', 'ZA'),
    ('+82', 'KR'),
    ('+34', 'ES'),
    ('+94', 'LK'),
    ('+46', 'SE'),
    ('+41', 'CH'),
    ('+963', 'SY'),
    ('+886', 'TW'),
    ('+992', 'TJ'),
    ('+255', 'TZ'),
    ('+66', 'TH'),
    ('+216', 'TN'),
    ('+993', 'TM'),
    ('+256', 'UG'),
    ('+380', 'UA'),
    ('+971', 'AE'),
    ('+44', 'GB'),
    ('+598', 'UY'),
    ('+998', 'UZ'),
    ('+58', 'VE'),
    ('+84', 'VN'),
    ('+967', 'YE'),
    ('+260', 'ZM'),
    ('+263', 'ZW'),
]

COUNTRY_DIAL_CODE_CHOICES = [
    (code, code)
    for code, _iso_code in COUNTRY_DIAL_CODES
]

COUNTRY_ISO_BY_CODE = {
    code: iso_code
    for code, iso_code in COUNTRY_DIAL_CODES
}


def country_flag_url(iso_code, size=40):
    return f'https://flagcdn.com/w{size}/{iso_code.lower()}.png'

_COUNTRY_CODES_SORTED = sorted(
    {code for code, _ in COUNTRY_DIAL_CODE_CHOICES},
    key=len,
    reverse=True,
)


def normalize_national_number(value):
    return re.sub(r'\D', '', (value or '').strip())


def validate_national_number(value, *, required=True):
    cleaned = normalize_national_number(value)
    if not cleaned:
        if required:
            raise ValueError('Telefon numarası zorunludur.')
        return ''

    if cleaned.startswith('0'):
        raise ValueError('Telefon numarasını başında 0 olmadan girin.')

    if not cleaned.isdigit():
        raise ValueError('Telefon numarası yalnızca rakam içermelidir.')

    if len(cleaned) < 6 or len(cleaned) > 15:
        raise ValueError('Geçerli bir telefon numarası girin.')

    return cleaned


def format_international_phone(country_code, national_number):
    national = validate_national_number(national_number, required=True)
    code = (country_code or DEFAULT_COUNTRY_CODE).strip()
    if not code.startswith('+'):
        code = f'+{code}'
    return f'{code}{national}'


def split_international_phone(full_phone, default_code=DEFAULT_COUNTRY_CODE):
    if not full_phone:
        return default_code, ''

    phone = str(full_phone).strip()
    if phone.startswith('+'):
        for code in _COUNTRY_CODES_SORTED:
            if phone.startswith(code):
                return code, phone[len(code):]

    cleaned = normalize_national_number(phone)
    if cleaned.startswith('0'):
        return default_code, cleaned[1:]

    return default_code, cleaned
