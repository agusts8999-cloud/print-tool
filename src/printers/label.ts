import { RasterImage } from "../types";

function bytesToHex(data: Buffer): string {
  return data.toString("hex").toUpperCase();
}

export function buildZplImagePayload(image: RasterImage): Buffer {
  const totalBytes = image.bitmap.length;
  const bytesPerRow = image.bytesPerRow;
  const hexData = bytesToHex(image.bitmap);

  // ^GFA: totalBytes, totalBytes, bytesPerRow, data
  // ^PW follows exact pixel width to match 58/80 mm conversion.
  const zpl = [
    "^XA",
    `^PW${image.width}`,
    "^LH0,0",
    "^FO0,0",
    `^GFA,${totalBytes},${totalBytes},${bytesPerRow},${hexData}`,
    "^XZ"
  ].join("\n");

  return Buffer.from(zpl, "ascii");
}
