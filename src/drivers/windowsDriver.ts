import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import PDFDocument from "pdfkit";
import { getPrinters, print } from "pdf-to-printer";

export async function listWindowsPrinters(): Promise<string[]> {
  const printers = await getPrinters();
  return printers.map((printer) => printer.name);
}

function mmToPt(mm: number): number {
  return (mm / 25.4) * 72;
}

async function writePdfFromPng(pngBuffer: Buffer, widthMm: number, heightMm: number, outputPath: string): Promise<void> {
  await new Promise<void>((resolve, reject) => {
    const doc = new PDFDocument({
      autoFirstPage: false,
      margins: { top: 0, left: 0, right: 0, bottom: 0 }
    });

    const chunks: Buffer[] = [];
    doc.on("data", (chunk: Buffer) => chunks.push(chunk));
    doc.on("error", reject);
    doc.on("end", async () => {
      try {
        await fs.writeFile(outputPath, Buffer.concat(chunks));
        resolve();
      } catch (err) {
        reject(err);
      }
    });

    const widthPt = mmToPt(widthMm);
    const heightPt = mmToPt(heightMm);
    doc.addPage({ size: [widthPt, heightPt], margin: 0 });
    doc.image(pngBuffer, 0, 0, { width: widthPt, height: heightPt });
    doc.end();
  });
}

export async function printViaWindowsDriver(params: {
  pngBuffer: Buffer;
  widthMm: number;
  heightMm: number;
  printerName?: string;
}): Promise<void> {
  const outputPath = path.join(os.tmpdir(), `print-bmp-${Date.now()}.pdf`);

  try {
    await writePdfFromPng(params.pngBuffer, params.widthMm, params.heightMm, outputPath);

    await print(outputPath, {
      printer: params.printerName
    });
  } finally {
    await fs.unlink(outputPath).catch(() => undefined);
  }
}
