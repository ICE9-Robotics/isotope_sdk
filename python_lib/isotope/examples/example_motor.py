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
usb_address = '/dev/cu.usbmodem2144101'


def validate_result(result: bool):
    if result:
        print("Execution was successful.")
    else:
        print("Execution failed.")


def main():
    # Start the communication
    isot = isotope.Isotope(usb_address, DEBUG_ENABLED, response_timeout=5)
    isot.connect()
    
    print(f"{len(isot.motors)} motor ports available.")

    # Iterate through all the MOT ports
    for motor in isot.motors:
        # Configure motor port
        result = motor.configure(resolution, current, rpm)
        validate_result(result)
        
        # Retrieve your settings
        print(f"Resolution: {motor.resolution}")
        print(f"Current: {motor.current}")
        print(f"RPM: {motor.rpm}")
        
        # Change your settings
        result = motor.set_current(300)
        result = result | motor.set_rpm(100)
        validate_result(result)

        # Enable the motor port
        result = motor.enable()

        if not result or not motor.is_enabled():
            raise Exception("Failed to enable motor port.")

        # Rotate the motor by 100 steps
        result = motor.rotate_by_steps(100)
        validate_result(result)
        
        # Rotate the motor by 90 degrees
        result = motor.rotate_by_degrees(90)
        validate_result(result)

        # Disable the motor port
        result = motor.disable()
        validate_result(result)

    # Close the connection
    isot.disconnect()


if __name__ == "__main__":
    main()
