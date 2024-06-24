import isotope
import time

DEBUG_ENABLED = True

# Power output port ID to be controlled
port_id = 1

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
    isot = isotope.Isotope(usb_address, DEBUG_ENABLED, response_timeout=5)
    isot.connect()

    # Get power output port at port_id
    port = isot.powers[port_id]

    print(f"Enable Port {port_id} with default PWM: {port.default_pwm}")
    result = port.enable()
    validate_result(result)
    time.sleep(0.1)

    print(f"Port {port_id} is {'enabled' if port.is_enabled() else 'disabled'}.")
    print(f"Current PWM value is {port.get_pwm()}")
        
    print("Change default PWM to 300")
    result = port.default_pwm = 300

    print(f"Enable Port {port_id} with a custom PWM value of 512")
    result = port.enable(512)
    validate_result(result)
    time.sleep(0.1)

    print(f"Disable Port {port_id}")
    result = port.disable()
    validate_result(result)

    # Close the connection
    isot.disconnect()


if __name__ == "__main__":
    main()
