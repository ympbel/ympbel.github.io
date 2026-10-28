import io

from PIL import Image

from crawl.images import shrink_image


def encode(image: Image.Image, fmt: str, **params) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, fmt, **params)
    return buffer.getvalue()


def decode(data: bytes) -> Image.Image:
    image = Image.open(io.BytesIO(data))
    image.load()
    return image


def test_large_jpeg_shrinks_to_800_long_edge():
    result = decode(shrink_image(encode(Image.new('RGB', (2000, 1200), 'red'), 'JPEG')))
    assert (result.format, result.size) == ('JPEG', (800, 480))


def test_small_png_is_returned_unchanged():
    data = encode(Image.new('RGB', (300, 200), 'blue'), 'PNG')
    assert shrink_image(data) == data


def test_rgba_png_stays_png_with_alpha():
    result = decode(shrink_image(encode(Image.new('RGBA', (1600, 1600), (0, 0, 255, 128)), 'PNG')))
    assert (result.format, result.size, result.mode) == ('PNG', (800, 800), 'RGBA')


def test_exif_rotation_is_applied_before_shrinking():
    # A camera photo stored landscape with "rotate 90" in EXIF; re-encoding drops the tag,
    # so the pixels must be turned upright first or the photo shows sideways.
    exif = Image.Exif()
    exif[0x0112] = 6
    result = decode(shrink_image(encode(Image.new('RGB', (2000, 1200), 'red'), 'JPEG', exif=exif)))
    assert result.size == (480, 800)
    assert result.getexif().get(0x0112, 1) == 1
