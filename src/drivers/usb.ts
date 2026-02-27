import { usb } from "usb";

export async function listUsbDevices(): Promise<string[]> {
  const devices = usb.getDeviceList();
  return devices.map((device) => {
    const dd = device.deviceDescriptor;
    const vid = dd.idVendor.toString(16).padStart(4, "0");
    const pid = dd.idProduct.toString(16).padStart(4, "0");
    return `VID:PID ${vid}:${pid}`;
  });
}

function parseHexId(id: number | string): number {
  if (typeof id === "number") {
    return id;
  }

  if (id.startsWith("0x") || id.startsWith("0X")) {
    return Number.parseInt(id.slice(2), 16);
  }

  if (/^[0-9a-fA-F]+$/.test(id)) {
    return Number.parseInt(id, 16);
  }

  return Number.parseInt(id, 10);
}

export async function sendRawToUsb(params: {
  vid: number | string;
  pid: number | string;
  payload: Buffer;
  interfaceNumber?: number;
}): Promise<void> {
  const vid = parseHexId(params.vid);
  const pid = parseHexId(params.pid);

  const device = usb.findByIds(vid, pid);
  if (!device) {
    throw new Error(`Device USB ${vid.toString(16)}:${pid.toString(16)} tidak ditemukan.`);
  }

  device.open();

  const ifaceIndex = params.interfaceNumber ?? 0;
  const iface = device.interfaces[ifaceIndex];
  if (!iface) {
    throw new Error(`Interface USB ${ifaceIndex} tidak tersedia.`);
  }

  if (iface.isKernelDriverActive?.()) {
    try {
      iface.detachKernelDriver();
    } catch {
      // Ignore if driver cannot be detached on current platform.
    }
  }

  iface.claim();
  const endpoint = iface.endpoints.find((ep) => ep.direction === "out");
  if (!endpoint) {
    iface.release(true, () => undefined);
    throw new Error("Endpoint OUT USB tidak ditemukan.");
  }

  await new Promise<void>((resolve, reject) => {
    endpoint.transfer(params.payload, (err) => {
      if (err) {
        reject(err);
        return;
      }
      resolve();
    });
  });

  await new Promise<void>((resolve) => iface.release(true, () => resolve()));
  device.close();
}
