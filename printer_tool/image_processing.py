from dataclasses import dataclass

from PIL import Image, ImageOps
from PIL import ImageEnhance

from .settings import get_paper_width_mm, get_printable_width_pixels


@dataclass
class RasterImage:
    width: int
    height: int
    bytes_per_row: int
    bitmap: bytes


def _pack_mono_bitmap(gray_image: Image.Image, threshold: int) -> bytes:
    width, height = gray_image.size
    pixels = gray_image.tobytes()
    bytes_per_row = width // 8
    out = bytearray(bytes_per_row * height)

    for y in range(height):
        for x_byte in range(bytes_per_row):
            value = 0
            for bit in range(8):
                x = x_byte * 8 + bit
                pixel = pixels[y * width + x]
                if pixel < threshold:
                    value |= 0x80 >> bit
            out[y * bytes_per_row + x_byte] = value

    return bytes(out)


def _apply_darkness(image: Image.Image, darkness: int) -> Image.Image:
    if darkness < 50 or darkness > 180:
        raise ValueError("darkness harus 50-180.")

    # 100 = netral, >100 lebih gelap, <100 lebih terang.
    brightness_factor = 100.0 / float(darkness)
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(brightness_factor)


def prepare_raster_image(file_path: str, paper: int, dpi: int, threshold: int, darkness: int = 100) -> RasterImage:
    if threshold < 0 or threshold > 255:
        raise ValueError("threshold harus 0-255.")

    target_width = get_printable_width_pixels(paper, dpi)
    image = Image.open(file_path)
    image = ImageOps.exif_transpose(image)
    image = image.convert("L")

    ratio = image.height / image.width
    resized_height = max(1, round(target_width * ratio))
    image = image.resize((target_width, resized_height), Image.Resampling.LANCZOS)
    image = _apply_darkness(image, darkness)

    bitmap = _pack_mono_bitmap(image, threshold)
    return RasterImage(
        width=target_width,
        height=resized_height,
        bytes_per_row=target_width // 8,
        bitmap=bitmap,
    )


def prepare_printable_rgb(file_path: str, paper: int, dpi: int, darkness: int = 100) -> tuple[Image.Image, float, float]:
    target_width = get_printable_width_pixels(paper, dpi)
    width_mm = float(get_paper_width_mm(paper))

    image = Image.open(file_path)
    image = ImageOps.exif_transpose(image)
    image = image.convert("RGB")

    ratio = image.height / image.width
    resized_height = max(1, round(target_width * ratio))
    image = image.resize((target_width, resized_height), Image.Resampling.LANCZOS)
    image = _apply_darkness(image, darkness)
    height_mm = (resized_height / dpi) * 25.4

    return image, width_mm, height_mm
