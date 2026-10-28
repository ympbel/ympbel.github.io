"""Downscaling of crawled photos (the reference cache keeps the untouched originals)."""
from __future__ import annotations

import io

from PIL import Image, ImageOps


def shrink_image(data: bytes, max_edge: int = 800) -> bytes:
    """`data` with its long edge cut to `max_edge` px, aspect kept, never upscaled.

    JPEG sources are saved as JPEG quality 85, PNG (and any other format) as optimized PNG.
    A JPEG or PNG that is already small enough comes back byte-identical. EXIF rotation is
    applied to the pixels first, because the re-encoded file carries no EXIF tag.
    """
    with Image.open(io.BytesIO(data)) as image:
        fmt = 'JPEG' if image.format in ('JPEG', 'MPO') else 'PNG'
        if max(image.size) <= max_edge and image.format in ('JPEG', 'PNG'):
            return data
        icc_profile = image.info.get('icc_profile')
        image = ImageOps.exif_transpose(image)
        if fmt == 'JPEG' and image.mode not in ('L', 'RGB', 'CMYK'):
            image = image.convert('RGB')
        elif fmt == 'PNG' and image.mode not in ('L', 'LA', 'RGB', 'RGBA'):
            image = image.convert('RGBA')  # P/1/I modes: LANCZOS needs real channels
        width, height = image.size
        scale = min(1.0, max_edge / max(width, height))
        if scale < 1:
            size = (max(1, round(width * scale)), max(1, round(height * scale)))
            image = image.resize(size, Image.Resampling.LANCZOS)
        out = io.BytesIO()
        params = {'quality': 85} if fmt == 'JPEG' else {'optimize': True}
        if icc_profile:
            params['icc_profile'] = icc_profile
        image.save(out, fmt, **params)
        return out.getvalue()
