from PIL import ImageWin

try:
    import win32con
    import win32print
    import win32ui
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("pywin32 belum terpasang. Jalankan: pip install pywin32") from exc


def list_windows_printers() -> list[str]:
    flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
    printers = win32print.EnumPrinters(flags)
    names = [item[2] for item in printers]
    names.sort()
    return names


def print_via_windows_driver(image, printer_name: str | None = None) -> None:
    target_printer = printer_name or win32print.GetDefaultPrinter()
    if not target_printer:
        raise RuntimeError("Tidak ada default printer Windows.")

    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(target_printer)

    printable_w = hdc.GetDeviceCaps(win32con.HORZRES)
    printable_h = hdc.GetDeviceCaps(win32con.VERTRES)

    src_w, src_h = image.size
    scale = min(printable_w / src_w, printable_h / src_h)
    dst_w = max(1, int(src_w * scale))
    dst_h = max(1, int(src_h * scale))

    x = max(0, (printable_w - dst_w) // 2)
    y = 0

    hdc.StartDoc("print-bmp")
    hdc.StartPage()
    dib = ImageWin.Dib(image)
    dib.draw(hdc.GetHandleOutput(), (x, y, x + dst_w, y + dst_h))
    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()

