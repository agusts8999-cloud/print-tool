MM_PER_INCH = 25.4


def mm_to_pixels(mm: float, dpi: int) -> int:
    return round((mm / MM_PER_INCH) * dpi)


def get_paper_width_mm(paper: int) -> int:
    if paper not in (58, 80):
        raise ValueError("Paper harus 58 atau 80.")
    return paper


def get_printable_width_pixels(paper: int, dpi: int) -> int:
    total_width = mm_to_pixels(get_paper_width_mm(paper), dpi)
    side_margin = round(total_width * 0.02)
    width = total_width - (side_margin * 2)
    return (width // 8) * 8

