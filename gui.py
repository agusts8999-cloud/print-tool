import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from printer_tool.image_processing import prepare_printable_rgb, prepare_raster_image
from printer_tool.printers import build_escpos_image_payload, build_zpl_image_payload
from printer_tool.usb_driver import list_usb_devices, send_raw_to_usb
from printer_tool.windows_driver import list_windows_printers, print_via_windows_driver


class PrinterToolGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Printer Tool")
        self.root.geometry("760x560")
        self.root.minsize(720, 520)

        self.file_path = tk.StringVar()
        self.mode = tk.StringVar(value="escpos")
        self.paper = tk.StringVar(value="58")
        self.connection = tk.StringVar(value="windows")
        self.printer_name = tk.StringVar()
        self.usb_vid = tk.StringVar()
        self.usb_pid = tk.StringVar()
        self.usb_interface = tk.StringVar(value="0")
        self.dpi = tk.StringVar(value="203")
        self.threshold = tk.StringVar(value="128")
        self.darkness = tk.IntVar(value=100)

        self.status = tk.StringVar(value="Siap.")

        self._build_ui()
        self._toggle_connection_fields()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(frame, text="Print BMP/Image Tool", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))

        ttk.Label(frame, text="File gambar").grid(row=1, column=0, sticky="w", pady=4)
        file_entry = ttk.Entry(frame, textvariable=self.file_path)
        file_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=8)
        ttk.Button(frame, text="Browse...", command=self._pick_file).grid(row=1, column=3, sticky="ew")

        ttk.Label(frame, text="Mode").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Combobox(frame, textvariable=self.mode, values=["escpos", "label"], state="readonly").grid(
            row=2, column=1, sticky="ew", padx=8
        )

        ttk.Label(frame, text="Paper (mm)").grid(row=2, column=2, sticky="w", pady=4)
        ttk.Combobox(frame, textvariable=self.paper, values=["58", "80"], state="readonly").grid(
            row=2, column=3, sticky="ew"
        )

        ttk.Label(frame, text="Koneksi").grid(row=3, column=0, sticky="w", pady=4)
        conn_combo = ttk.Combobox(frame, textvariable=self.connection, values=["windows", "usb"], state="readonly")
        conn_combo.grid(row=3, column=1, sticky="ew", padx=8)
        conn_combo.bind("<<ComboboxSelected>>", lambda _: self._toggle_connection_fields())

        ttk.Label(frame, text="DPI").grid(row=3, column=2, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.dpi).grid(row=3, column=3, sticky="ew")

        ttk.Label(frame, text="Threshold").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.threshold).grid(row=4, column=1, sticky="ew", padx=8)

        ttk.Label(frame, text="USB Interface").grid(row=4, column=2, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.usb_interface).grid(row=4, column=3, sticky="ew")

        ttk.Label(frame, text="Darkness").grid(row=5, column=0, sticky="w", pady=4)
        dark_scale = ttk.Scale(frame, from_=50, to=180, variable=self.darkness, orient="horizontal")
        dark_scale.grid(row=5, column=1, columnspan=2, sticky="ew", padx=8)
        self.darkness_label = ttk.Label(frame, text="100")
        self.darkness_label.grid(row=5, column=3, sticky="w")
        dark_scale.configure(command=self._on_darkness_change)

        sep = ttk.Separator(frame, orient="horizontal")
        sep.grid(row=6, column=0, columnspan=4, sticky="ew", pady=12)

        ttk.Label(frame, text="Printer Windows").grid(row=7, column=0, sticky="w", pady=4)
        self.printer_combo = ttk.Combobox(frame, textvariable=self.printer_name, state="readonly")
        self.printer_combo.grid(row=7, column=1, columnspan=2, sticky="ew", padx=8)
        ttk.Button(frame, text="Refresh Printer", command=self._load_printers).grid(row=7, column=3, sticky="ew")

        ttk.Label(frame, text="USB VID").grid(row=8, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.usb_vid).grid(row=8, column=1, sticky="ew", padx=8)
        ttk.Label(frame, text="USB PID").grid(row=8, column=2, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.usb_pid).grid(row=8, column=3, sticky="ew")

        ttk.Label(frame, text="Daftar USB").grid(row=9, column=0, sticky="nw", pady=(8, 4))
        self.usb_list = tk.Listbox(frame, height=10)
        self.usb_list.grid(row=9, column=1, columnspan=2, sticky="nsew", padx=8)
        ttk.Button(frame, text="Refresh USB", command=self._load_usb).grid(row=9, column=3, sticky="new")

        button_row = ttk.Frame(frame)
        button_row.grid(row=10, column=0, columnspan=4, sticky="ew", pady=(12, 8))
        ttk.Button(button_row, text="Print", command=self._start_print).pack(side="right")

        status = ttk.Label(frame, textvariable=self.status, anchor="w")
        status.grid(row=11, column=0, columnspan=4, sticky="ew")

        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(9, weight=1)

        self._load_printers()
        self._load_usb()

    def _set_status(self, text: str) -> None:
        self.status.set(text)
        self.root.update_idletasks()

    def _on_darkness_change(self, value: str) -> None:
        self.darkness_label.configure(text=str(int(float(value))))

    def _pick_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Pilih file gambar",
            filetypes=[
                ("Image", "*.bmp *.png *.jpg *.jpeg *.webp"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.file_path.set(path)

    def _toggle_connection_fields(self) -> None:
        is_windows = self.connection.get() == "windows"
        printer_state = "readonly" if is_windows else "disabled"
        usb_state = "disabled" if is_windows else "normal"

        self.printer_combo.configure(state=printer_state)

        for widget in (self.usb_list,):
            widget.configure(state=usb_state)

    def _load_printers(self) -> None:
        try:
            printers = list_windows_printers()
        except Exception as exc:
            messagebox.showerror("Error", f"Gagal ambil daftar printer:\n{exc}")
            return

        self.printer_combo["values"] = printers
        if printers and not self.printer_name.get():
            self.printer_name.set(printers[0])

    def _load_usb(self) -> None:
        self.usb_list.delete(0, tk.END)
        try:
            devices = list_usb_devices()
        except Exception as exc:
            messagebox.showerror("Error", f"Gagal ambil daftar USB:\n{exc}")
            return

        for dev in devices:
            self.usb_list.insert(tk.END, dev)

    def _start_print(self) -> None:
        thread = threading.Thread(target=self._print_job, daemon=True)
        thread.start()

    def _print_job(self) -> None:
        try:
            file_path = Path(self.file_path.get()).expanduser().resolve()
            if not file_path.exists():
                raise FileNotFoundError("File gambar belum dipilih atau tidak ditemukan.")

            mode = self.mode.get().strip().lower()
            paper = int(self.paper.get())
            connection = self.connection.get().strip().lower()
            dpi = int(self.dpi.get())
            threshold = int(self.threshold.get())
            darkness = int(self.darkness.get())
            usb_interface = int(self.usb_interface.get())

            self._set_status("Memproses gambar...")

            if connection == "windows":
                image, _, _ = prepare_printable_rgb(str(file_path), paper, dpi, darkness)
                self._set_status("Mengirim ke printer Windows...")
                print_via_windows_driver(image, self.printer_name.get().strip() or None)
            else:
                vid = self.usb_vid.get().strip()
                pid = self.usb_pid.get().strip()
                if not vid or not pid:
                    raise ValueError("USB VID dan PID wajib diisi untuk koneksi USB.")

                raster = prepare_raster_image(str(file_path), paper, dpi, threshold, darkness)
                if mode == "escpos":
                    payload = build_escpos_image_payload(raster)
                elif mode == "label":
                    payload = build_zpl_image_payload(raster)
                else:
                    raise ValueError("Mode harus escpos atau label.")

                self._set_status("Mengirim payload ke USB printer...")
                send_raw_to_usb(vid, pid, payload, usb_interface)

            self._set_status("Print job berhasil dikirim.")
            messagebox.showinfo("Sukses", "Print job berhasil dikirim.")
        except Exception as exc:
            self._set_status("Terjadi error.")
            messagebox.showerror("Error", str(exc))


def main() -> None:
    root = tk.Tk()
    app = PrinterToolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
