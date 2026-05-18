from __future__ import annotations

import hashlib
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


def placeholder_image(filename: str, label: str, *, width: int = 600, height: int = 600) -> ContentFile:
    """Generate a deterministic placeholder JPEG (no external network)."""
    digest = hashlib.md5(label.encode()).hexdigest()
    r, g, b = int(digest[0:2], 16), int(digest[2:4], 16), int(digest[4:6], 16)
    img = Image.new('RGB', (width, height), (r, g, b))
    draw = ImageDraw.Draw(img)
    text = label[:28]
    draw.rectangle([20, 20, width - 20, height - 20], outline=(255, 255, 255), width=3)
    draw.text((40, height // 2 - 10), text, fill=(255, 255, 255))
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return ContentFile(buf.getvalue(), name=filename)
