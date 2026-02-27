from .image_processing import RasterImage


def build_escpos_image_payload(image: RasterImage) -> bytes:
    chunks = []

    chunks.append(bytes([0x1B, 0x40]))  # Init
    chunks.append(bytes([0x1B, 0x61, 0x01]))  # Center align

    width_bytes = image.bytes_per_row
    x_l = width_bytes & 0xFF
    x_h = (width_bytes >> 8) & 0xFF
    y_l = image.height & 0xFF
    y_h = (image.height >> 8) & 0xFF

    chunks.append(bytes([0x1D, 0x76, 0x30, 0x00, x_l, x_h, y_l, y_h]))
    chunks.append(image.bitmap)
    chunks.append(bytes([0x0A, 0x0A, 0x0A]))
    chunks.append(bytes([0x1D, 0x56, 0x00]))  # Full cut

    return b"".join(chunks)


def build_zpl_image_payload(image: RasterImage) -> bytes:
    total_bytes = len(image.bitmap)
    bytes_per_row = image.bytes_per_row
    hex_data = image.bitmap.hex().upper()

    zpl = "\n".join(
        [
            "^XA",
            f"^PW{image.width}",
            "^LH0,0",
            "^FO0,0",
            f"^GFA,{total_bytes},{total_bytes},{bytes_per_row},{hex_data}",
            "^XZ",
        ]
    )
    return zpl.encode("ascii")

