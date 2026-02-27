import libusb_package
import usb.core
import usb.util


def _parse_usb_id(value: str) -> int:
    lowered = value.lower()
    if lowered.startswith("0x"):
        return int(lowered[2:], 16)
    if any(ch in "abcdef" for ch in lowered):
        return int(lowered, 16)
    return int(lowered, 10)


def _usb_backend():
    return libusb_package.get_libusb1_backend()


def list_usb_devices() -> list[str]:
    devices = usb.core.find(find_all=True, backend=_usb_backend())
    rows: list[str] = []
    for dev in devices:
        rows.append(f"VID:PID {dev.idVendor:04x}:{dev.idProduct:04x}")
    return rows


def send_raw_to_usb(vid: str, pid: str, payload: bytes, interface_number: int = 0) -> None:
    vid_id = _parse_usb_id(vid)
    pid_id = _parse_usb_id(pid)

    backend = _usb_backend()
    device = usb.core.find(idVendor=vid_id, idProduct=pid_id, backend=backend)
    if device is None:
        raise RuntimeError(f"Device USB {vid_id:04x}:{pid_id:04x} tidak ditemukan.")

    device.set_configuration()
    cfg = device.get_active_configuration()
    intf = cfg[(interface_number, 0)]

    endpoint = None
    for ep in intf.endpoints():
        if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
            endpoint = ep
            break

    if endpoint is None:
        raise RuntimeError("Endpoint OUT USB tidak ditemukan.")

    endpoint.write(payload)
    usb.util.dispose_resources(device)
