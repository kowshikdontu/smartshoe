import evdev
import threading

# Replace these with the actual event codes for left and right taps
LEFT_TAP_EVENT_CODE = evdev.ecodes.KEY_PAUSECD
double_TAP_EVENT_CODE = evdev.ecodes.KEY_NEXTSONG

# Replace "/dev/input/eventX" with the actual device path of your Bluetooth earbuds
device_path = "/dev/input/event1"

# Create an evdev device instance
device = evdev.InputDevice(device_path)

# Thread functions to be triggered on left and right taps
def left_tap_thread_func():
    print("Left Tap Event Triggered")
    # Implement your left tap logic here

def right_tap_thread_func():
    print("Right Tap Event Triggered")
    # Implement your right tap logic here

# Read input events
for event in device.read_loop():
    if event.type == evdev.ecodes.EV_KEY:
        if event.code == LEFT_TAP_EVENT_CODE and event.value == 1:
            # Left tap event detected
            left_tap_thread = threading.Thread(target=left_tap_thread_func)
            left_tap_thread.start()
        elif event.code == double_TAP_EVENT_CODE and event.value == 1:
            # Right tap event detected
            right_tap_thread = threading.Thread(target=right_tap_thread_func)
            right_tap_thread.start()
