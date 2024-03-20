import bluetooth
from bluetooth.btcommon import BluetoothError

def discover_devices():
    try:
        nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, lookup_class=True, device_id=-1, device_name=None, device_class=None, device_id_pattern=None, lookup_oui=True, device_oui=None)
        return nearby_devices
    except BluetoothError as e:
        print(f"Bluetooth error: {e}")
        return []

def handle_event(device_info):
    print("Bluetooth Event Detected:")
    print(f"Device Name: {device_info[1]}")
    print(f"Device Address: {device_info[0]}")
    print(f"Device Class: {device_info[2]}")
    print("------------------------")

    # Add your event handling logic here
    # For example, send an emergency message or perform other actions based on the device_info

def main():
    print("Scanning for Bluetooth devices...")
    devices = discover_devices()

    if devices:
        for device_info in devices:
            handle_event(device_info)
    else:
        print("No Bluetooth devices found.")

if __name__ == "__main__":
    main()
