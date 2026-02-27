export type PrinterMode = "escpos" | "label";
export type ConnectionType = "usb" | "windows";
export type PaperSize = 58 | 80;

export interface PrintOptions {
  file: string;
  mode: PrinterMode;
  paper: PaperSize;
  connection: ConnectionType;
  dpi: number;
  threshold: number;
  printerName?: string;
  usbVid?: number;
  usbPid?: number;
  usbInterface?: number;
}

export interface RasterImage {
  width: number;
  height: number;
  bytesPerRow: number;
  bitmap: Buffer;
}
