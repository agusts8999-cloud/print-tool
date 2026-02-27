import argparse
from pathlib import Path

from printer_tool.image_processing import prepare_printable_rgb, prepare_raster_image
from printer_tool.printers import build_escpos_image_payload, build_zpl_image_payload
from printer_tool.usb_driver import list_usb_devices, send_raw_to_usb
from printer_tool.windows_driver import list_windows_printers, print_via_windows_driver


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print image files to ESC/POS or label printers")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-printers", help="List Windows printers")
    sub.add_parser("list-usb", help="List connected USB devices")

    p_print = sub.add_parser("print", help="Print image")
    p_print.add_argument("--file", required=True, help="Path file gambar")
    p_print.add_argument("--mode", required=True, choices=["escpos", "label"], help="Mode printer")
    p_print.add_argument("--paper", required=True, type=int, choices=[58, 80], help="Lebar kertas (mm)")
    p_print.add_argument("--connection", required=True, choices=["usb", "windows"], help="Jenis koneksi")
    p_print.add_argument("--printer-name", help="Nama printer Windows")
    p_print.add_argument("--usb-vid", help="USB Vendor ID, contoh 0x04b8")
    p_print.add_argument("--usb-pid", help="USB Product ID, contoh 0x0e15")
    p_print.add_argument("--usb-interface", type=int, default=0, help="USB interface index")
    p_print.add_argument("--dpi", type=int, default=203, help="Target DPI")
    p_print.add_argument("--threshold", type=int, default=128, help="Threshold BW 0-255")
    p_print.add_argument("--darkness", type=int, default=100, help="Kepekatan/gelap 50-180 (100 netral)")

    return parser.parse_args()


def command_list_printers() -> int:
    printers = list_windows_printers()
    if not printers:
        print("Tidak ada printer Windows yang terdeteksi.")
        return 0

    for printer in printers:
        print(printer)
    return 0


def command_list_usb() -> int:
    devices = list_usb_devices()
    if not devices:
        print("Tidak ada device USB yang terdeteksi.")
        return 0

    for device in devices:
        print(device)
    return 0


def command_print(args: argparse.Namespace) -> int:
    file_path = Path(args.file).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

    if args.connection == "windows":
        image, _, _ = prepare_printable_rgb(str(file_path), args.paper, args.dpi, args.darkness)
        print_via_windows_driver(image, args.printer_name)
        print("Print job berhasil dikirim.")
        return 0

    if not args.usb_vid or not args.usb_pid:
        raise ValueError("Untuk koneksi USB, wajib isi --usb-vid dan --usb-pid.")

    raster = prepare_raster_image(str(file_path), args.paper, args.dpi, args.threshold, args.darkness)
    if args.mode == "escpos":
        payload = build_escpos_image_payload(raster)
    else:
        payload = build_zpl_image_payload(raster)

    send_raw_to_usb(args.usb_vid, args.usb_pid, payload, args.usb_interface)
    print("Print job berhasil dikirim.")
    return 0


def main() -> int:
    args = parse_args()

    if args.command == "list-printers":
        return command_list_printers()
    if args.command == "list-usb":
        return command_list_usb()
    if args.command == "print":
        return command_print(args)

    raise ValueError(f"Command tidak dikenal: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
