#!/usr/bin/env node

import { Command } from "commander";
import path from "node:path";
import fs from "node:fs/promises";
import { preparePrintablePng, prepareRasterImage } from "./utils/imageProcessing";
import { buildEscPosImagePayload } from "./printers/escpos";
import { buildZplImagePayload } from "./printers/label";
import { listUsbDevices, sendRawToUsb } from "./drivers/usb";
import { listWindowsPrinters, printViaWindowsDriver } from "./drivers/windowsDriver";
import { ConnectionType, PaperSize, PrinterMode, PrintOptions } from "./types";

function parsePaper(value: string): PaperSize {
  if (value === "58" || value === "80") {
    return Number(value) as PaperSize;
  }
  throw new Error("Paper harus 58 atau 80.");
}

function parseConnection(value: string): ConnectionType {
  if (value === "usb" || value === "windows") {
    return value;
  }
  throw new Error("Connection harus usb atau windows.");
}

function parseMode(value: string): PrinterMode {
  if (value === "escpos" || value === "label") {
    return value;
  }
  throw new Error("Mode harus escpos atau label.");
}

function parseNumber(value: string, fieldName: string): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    throw new Error(`${fieldName} tidak valid: ${value}`);
  }
  return parsed;
}

function parseUsbId(value: string): number {
  if (value.startsWith("0x") || value.startsWith("0X")) {
    return Number.parseInt(value.slice(2), 16);
  }
  if (/[a-fA-F]/.test(value)) {
    return Number.parseInt(value, 16);
  }
  return Number.parseInt(value, 10);
}

async function ensureFileExists(filePath: string): Promise<void> {
  await fs.access(filePath);
}

async function doPrint(options: PrintOptions): Promise<void> {
  await ensureFileExists(options.file);

  if (options.connection === "windows") {
    const printable = await preparePrintablePng(options.file, options.paper, options.dpi);
    await printViaWindowsDriver({
      pngBuffer: printable.pngBuffer,
      widthMm: printable.widthMm,
      heightMm: printable.heightMm,
      printerName: options.printerName
    });
    return;
  }

  if (options.usbVid === undefined || options.usbPid === undefined) {
    throw new Error("Untuk koneksi USB, wajib isi --usb-vid dan --usb-pid.");
  }

  const raster = await prepareRasterImage({
    filePath: options.file,
    paper: options.paper,
    dpi: options.dpi,
    threshold: options.threshold
  });

  const payload = options.mode === "escpos" ? buildEscPosImagePayload(raster) : buildZplImagePayload(raster);

  await sendRawToUsb({
    vid: options.usbVid,
    pid: options.usbPid,
    payload,
    interfaceNumber: options.usbInterface
  });
}

async function run(): Promise<void> {
  const program = new Command();
  program.name("printer-tool").description("Print image files to ESC/POS or label printers");

  program
    .command("list-printers")
    .description("List Windows printers")
    .action(async () => {
      const printers = await listWindowsPrinters();
      if (printers.length === 0) {
        console.log("Tidak ada printer Windows yang terdeteksi.");
        return;
      }
      printers.forEach((name) => console.log(name));
    });

  program
    .command("list-usb")
    .description("List connected USB devices as VID:PID")
    .action(async () => {
      const devices = await listUsbDevices();
      if (devices.length === 0) {
        console.log("Tidak ada device USB yang terdeteksi.");
        return;
      }
      devices.forEach((entry) => console.log(entry));
    });

  program
    .command("print")
    .description("Print image")
    .requiredOption("--file <path>", "Path file gambar")
    .requiredOption("--mode <escpos|label>", "Mode printer")
    .requiredOption("--paper <58|80>", "Lebar kertas dalam mm")
    .requiredOption("--connection <usb|windows>", "Jenis koneksi")
    .option("--printer-name <name>", "Nama printer Windows")
    .option("--usb-vid <vid>", "USB Vendor ID, contoh 0x04b8")
    .option("--usb-pid <pid>", "USB Product ID, contoh 0x0e15")
    .option("--usb-interface <index>", "USB interface index", "0")
    .option("--dpi <dpi>", "Target DPI", "203")
    .option("--threshold <0-255>", "Threshold BW", "128")
    .action(async (raw) => {
      const file = path.resolve(String(raw.file));
      const mode = parseMode(String(raw.mode));
      const paper = parsePaper(String(raw.paper));
      const connection = parseConnection(String(raw.connection));
      const dpi = parseNumber(String(raw.dpi), "dpi");
      const threshold = parseNumber(String(raw.threshold), "threshold");
      const usbInterface = parseNumber(String(raw.usbInterface), "usb-interface");

      const options: PrintOptions = {
        file,
        mode,
        paper,
        connection,
        dpi,
        threshold,
        printerName: raw.printerName ? String(raw.printerName) : undefined,
        usbVid: raw.usbVid ? parseUsbId(String(raw.usbVid)) : undefined,
        usbPid: raw.usbPid ? parseUsbId(String(raw.usbPid)) : undefined,
        usbInterface
      };

      await doPrint(options);
      console.log("Print job berhasil dikirim.");
    });

  await program.parseAsync(process.argv);
}

run().catch((err) => {
  console.error(`Error: ${(err as Error).message}`);
  process.exit(1);
});
