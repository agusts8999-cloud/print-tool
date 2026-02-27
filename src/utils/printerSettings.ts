import { PaperSize } from "../types";

export const MM_PER_INCH = 25.4;

export function mmToPixels(mm: number, dpi: number): number {
  return Math.round((mm / MM_PER_INCH) * dpi);
}

export function getPaperWidthMm(paper: PaperSize): number {
  if (paper === 58) {
    return 58;
  }
  return 80;
}

export function getPrintableWidthPixels(paper: PaperSize, dpi: number): number {
  const totalWidth = mmToPixels(getPaperWidthMm(paper), dpi);
  const sideMargin = Math.round(totalWidth * 0.02);
  const width = totalWidth - sideMargin * 2;

  // ESC/POS raster image is byte-aligned in width.
  return Math.floor(width / 8) * 8;
}
