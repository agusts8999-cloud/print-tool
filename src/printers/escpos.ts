import { RasterImage } from "../types";

export function buildEscPosImagePayload(image: RasterImage): Buffer {
  const chunks: Buffer[] = [];

  // Initialize printer.
  chunks.push(Buffer.from([0x1b, 0x40]));

  // Center align.
  chunks.push(Buffer.from([0x1b, 0x61, 0x01]));

  // GS v 0
  // m=0, xL xH (bytes), yL yH (dots)
  const widthBytes = image.bytesPerRow;
  const xL = widthBytes & 0xff;
  const xH = (widthBytes >> 8) & 0xff;
  const yL = image.height & 0xff;
  const yH = (image.height >> 8) & 0xff;

  chunks.push(Buffer.from([0x1d, 0x76, 0x30, 0x00, xL, xH, yL, yH]));
  chunks.push(image.bitmap);

  // Feed and cut.
  chunks.push(Buffer.from([0x0a, 0x0a, 0x0a]));
  chunks.push(Buffer.from([0x1d, 0x56, 0x00]));

  return Buffer.concat(chunks);
}
