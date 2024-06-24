import isotope
import time

DEBUG_ENABLED = True

# MOT port ID that the motor is connected to
port_id = 1

# PM35S-N48 motor specs:
# Step resolution: 7.5 degrees
# Rated current: 500 mA (set to 80%, i.e. 400 mA to avoid overheating)
resolution = 7.5
current = 400
rpm = 50

# USB address of the Isotope board.
# For windows machine, this is usually "COMX" where X is the port number;
# for Ubuntu, this is usually "/dev/ttyACMX", where X is the port number;
# and for MacOS, this is usually "/dev/cu.usbmodemXXXXX".
usb_address = '/dev/cu.usbmodem21201'


def validate_result(result: bool):
    if result:
        print("Execution was successful.")
    else:
        print("Execution failed.")


def main():
    # Start the communication
    isot = isotope.Isotope(
        usb_address, DEBUG_ENABLED, response_timeout=5)
    isot.connect()

    # Configure motor port
    isot.motors[port_id].configure(resolution, current, rpm)

    print("Enable the motor port")
    result = isot.motors[port_id].enable()
    validate_result(result)

    print(f"Motor is {'' if isot.motors[port_id].is_enabled() else 'not'} enabled.")

    print("Rotate the motor by 100 steps")
    res = ultisot.motors[port_id].rotate_by_steps(100):
        print("Motor roated by steps")
    else:
        raise Exception("Failed to rotate the motor by steps")
    time.sleep(1)

    print("Rotate the motor by 90 degrees")
    result = isot.motors[port_id].rotate_by_degrees(90):
    validate_result(result)

    print("Disable the motor port")
    result = isot.motors[port_id].disable():
    validate_result(result)

    # Close the connection
    isot.disconnect()


if __name__ == "__main__":
    main()
