# Print Tool (Python, Windows)

Tool desktop + CLI untuk mencetak file gambar (`BMP/PNG/JPG`) ke:
- Printer thermal ESC/POS
- Printer label (ZPL raw)

Koneksi yang didukung:
- `windows` (via driver Windows/GDI)
- `usb` raw (VID/PID)

Ukuran roll:
- `58mm`
- `80mm`

Tambahan fitur:
- Slider `Darkness` (kepekatan cetak) di GUI

## 1. Fitur Utama

- GUI sederhana untuk user operasional (pilih file, printer, mode, kertas, darkness)
- CLI untuk automasi/script
- Mode `escpos` (payload raster ESC/POS)
- Mode `label` (payload ZPL `^GFA`)
- Resize otomatis sesuai lebar 58/80mm
- Konversi image ke hitam-putih untuk thermal printing
- Pengaturan `threshold` dan `darkness`

## 2. Teknologi

- Python 3.11+ (tested di Python 3.13 pada Windows)
- Pillow (olah gambar)
- pywin32 (print via Windows driver)
- pyusb + libusb-package (USB raw)
- Tkinter (GUI)
- PyInstaller (build `.exe`)

## 3. Struktur Project

```text
printer-tool/
  printer_tool/
    image_processing.py
    printers.py
    usb_driver.py
    windows_driver.py
    settings.py
  main.py                # CLI entry
  gui.py                 # GUI entry
  build-windows.ps1      # setup virtualenv + install deps
  run-printer-tool.ps1   # jalankan CLI via .venv
  build-exe.ps1          # build EXE (GUI + CLI)
  requirements.txt
```

## 4. Prasyarat

- Windows 10/11
- Python 3.11+ 64-bit
- PowerShell

Cek Python:

```powershell
python --version
```

Jika tidak ada, install dari python.org lalu buka ulang terminal.

## 5. Setup Development

Dari folder project:

```powershell
cd C:\Users\Gene\Desktop\print_bmp\printer-tool
.\build-windows.ps1
```

Script ini akan:
- membuat virtual environment `.venv`
- upgrade `pip`
- install dependency dari `requirements.txt`

## 6. Tutorial GUI (Disarankan untuk Operasional)

Jalankan GUI:

```powershell
.\.venv\Scripts\python.exe .\gui.py
```

Langkah pakai:
1. Klik `Browse...` lalu pilih file gambar.
2. Pilih `Mode`:
   - `escpos` untuk printer thermal ESC/POS
   - `label` untuk printer label ZPL
3. Pilih `Paper`: `58` atau `80`.
4. Pilih `Koneksi`:
   - `windows`: pilih printer di dropdown `Printer Windows`
   - `usb`: isi `USB VID`, `USB PID`, dan `USB Interface`
5. Atur `DPI` (umumnya 203), `Threshold`, dan slider `Darkness`.
6. Klik `Print`.

Tips setelan:
- `Darkness` default `100`
- Nilai >100 membuat hasil lebih gelap
- Nilai <100 membuat hasil lebih terang
- `Threshold` biasanya stabil di `110-150` untuk thermal

## 7. Tutorial CLI

### 7.1 Cek daftar printer Windows

```powershell
.\run-printer-tool.ps1 list-printers
```

### 7.2 Cek daftar USB (VID:PID)

```powershell
.\run-printer-tool.ps1 list-usb
```

### 7.3 Print via Windows driver

```powershell
.\run-printer-tool.ps1 print `
  --file "C:\path\gambar.png" `
  --mode escpos `
  --paper 58 `
  --connection windows `
  --printer-name "POS-58" `
  --dpi 203 `
  --threshold 128 `
  --darkness 110
```

### 7.4 Print via USB raw (ESC/POS)

```powershell
.\run-printer-tool.ps1 print `
  --file "C:\path\gambar.bmp" `
  --mode escpos `
  --paper 80 `
  --connection usb `
  --usb-vid 0x04b8 `
  --usb-pid 0x0e15 `
  --usb-interface 0 `
  --dpi 203 `
  --threshold 128 `
  --darkness 115
```

### 7.5 Print via USB raw (Label/ZPL)

```powershell
.\run-printer-tool.ps1 print `
  --file "C:\path\label.png" `
  --mode label `
  --paper 58 `
  --connection usb `
  --usb-vid 0xXXXX `
  --usb-pid 0xYYYY `
  --usb-interface 0
```

## 8. Parameter CLI Lengkap

- `--file` path file gambar (wajib)
- `--mode` `escpos|label` (wajib)
- `--paper` `58|80` (wajib)
- `--connection` `usb|windows` (wajib)
- `--printer-name` nama printer Windows
- `--usb-vid` VID USB (hex `0x...` atau desimal)
- `--usb-pid` PID USB (hex `0x...` atau desimal)
- `--usb-interface` default `0`
- `--dpi` default `203`
- `--threshold` default `128` (0-255)
- `--darkness` default `100` (50-180)

## 9. Build EXE

Build executable GUI dan CLI:

```powershell
.\build-exe.ps1
```

Hasil build:
- `dist-exe\printer-tool-gui.exe`
- `dist-exe\printer-tool-cli.exe`

## 10. Jalankan EXE

GUI:

```powershell
.\dist-exe\printer-tool-gui.exe
```

CLI:

```powershell
.\dist-exe\printer-tool-cli.exe list-printers
.\dist-exe\printer-tool-cli.exe list-usb
```

## 11. Troubleshooting

### USB tidak terdeteksi / error backend
- Pastikan dependency `libusb-package` terinstall.
- Coba jalankan sebagai Administrator.
- Cek ulang VID/PID dari `list-usb`.

### Print USB gagal kirim payload
- Pastikan printer benar di mode raw command.
- Coba `--usb-interface 0` lalu alternatif `1`.

### Hasil terlalu pucat / terlalu hitam
- Ubah `--darkness` (100 -> 110/120 untuk lebih gelap).
- Ubah `--threshold` (turun untuk lebih banyak area hitam).

### Mode label tidak jalan
- Mode label saat ini memakai ZPL (`^GFA`).
- Jika printer Anda TSPL/CPCL/EPL, perlu backend command language lain.

## 12. Catatan Penting

- Untuk koneksi `windows`, mode `escpos/label` tidak mengubah protokol driver; yang dikirim adalah image via GDI.
- Untuk koneksi `usb`, mode menentukan payload raw:
  - `escpos` -> ESC/POS raster
  - `label` -> ZPL

## 13. Pengembangan Lanjutan (Opsional)

- Tambah preview live image di GUI sebelum print
- Simpan preset per printer (DPI, threshold, darkness, paper)
- Tambah backend label lain: TSPL/CPCL/EPL
