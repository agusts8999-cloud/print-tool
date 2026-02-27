import sharp from "sharp";
import { RasterImage } from "../types";
import { getPrintableWidthPixels, getPaperWidthMm, mmToPixels } from "./printerSettings";

interface PrepareImageParams {
  filePath: string;
  paper: 58 | 80;
  dpi: number;
  threshold: number;
}

function packMonoBitmap(gray: Buffer, width: number, height: number, threshold: number): Buffer {
  const bytesPerRow = width / 8;
  const output = Buffer.alloc(bytesPerRow * height);

  for (let y = 0; y < height; y += 1) {
    for (let xByte = 0; xByte < bytesPerRow; xByte += 1) {
      let byte = 0;

      for (let bit = 0; bit < 8; bit += 1) {
        const x = xByte * 8 + bit;
        const pixel = gray[y * width + x];
        const isBlack = pixel < threshold;
        if (isBlack) {
          byte |= 0x80 >> bit;
        }
      }

      output[y * bytesPerRow + xByte] = byte;
    }
  }

  return output;
}

export async function prepareRasterImage(params: PrepareImageParams): Promise<RasterImage> {
  const targetWidth = getPrintableWidthPixels(params.paper, params.dpi);
  const image = sharp(params.filePath).rotate();
  const metadata = await image.metadata();

  if (!metadata.width || !metadata.height) {
    throw new Error("File gambar tidak valid.");
  }

  const resizedHeight = Math.max(1, Math.round((metadata.height * targetWidth) / metadata.width));
  const { data } = await image
    .resize({ width: targetWidth, height: resizedHeight, fit: "inside" })
    .grayscale()
    .raw()
    .toBuffer({ resolveWithObject: true });

  const bytesPerRow = targetWidth / 8;
  const bitmap = packMonoBitmap(data, targetWidth, resizedHeight, params.threshold);

  return {
    width: targetWidth,
    height: resizedHeight,
    bytesPerRow,
    bitmap
  };
}

export async function preparePrintablePng(
  filePath: string,
  paper: 58 | 80,
  dpi: number
): Promise<{ pngBuffer: Buffer; widthMm: number; heightMm: number }> {
  const targetWidth = getPrintableWidthPixels(paper, dpi);
  const image = sharp(filePath).rotate();
  const metadata = await image.metadata();

  if (!metadata.width || !metadata.height) {
    throw new Error("File gambar tidak valid.");
  }

  const resizedHeight = Math.max(1, Math.round((metadata.height * targetWidth) / metadata.width));
  const pngBuffer = await image.resize({ width: targetWidth, height: resizedHeight, fit: "inside" }).png().toBuffer();

  const widthMm = getPaperWidthMm(paper);
  const heightMm = (resizedHeight / dpi) * 25.4;

  // Fallback in case metadata or resize behaves unexpectedly.
  if (!Number.isFinite(heightMm) || heightMm <= 0) {
    return {
      pngBuffer,
      widthMm,
      heightMm: (mmToPixels(widthMm, dpi) / dpi) * 25.4
    };
  }

  return { pngBuffer, widthMm, heightMm };
}
