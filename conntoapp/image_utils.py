from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image

PROFILE_IMAGE_SIZE = 400


def normalize_profile_image(uploaded_file):
    """Profil fotoğrafını merkezden kare kırpar ve standart boyuta getirir."""
    uploaded_file.seek(0)
    image = Image.open(uploaded_file)
    image = image.convert('RGB') if image.mode in ('RGBA', 'LA', 'P') else image

    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    image = image.crop((left, top, left + side, top + side))
    image = image.resize(
        (PROFILE_IMAGE_SIZE, PROFILE_IMAGE_SIZE),
        Image.Resampling.LANCZOS,
    )

    buffer = BytesIO()
    image.save(buffer, format='JPEG', quality=85, optimize=True)
    buffer.seek(0)

    original_name = getattr(uploaded_file, 'name', 'profile.jpg') or 'profile.jpg'
    base_name = original_name.rsplit('.', 1)[0]
    return ContentFile(buffer.read(), name=f'{base_name}.jpg')
