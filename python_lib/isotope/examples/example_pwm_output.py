import isotope
import time

DEBUG_ENABLED = True

# PWM output port ID to be controlled
port_id = 1

# USB address of the Isotope board.
# For windows machine, this is usually "COMX" where X is the port number;
# for Ubuntu, this is usually "/dev/ttyACMX", where X is the port number;
# and for MacOS, this is usually "/dev/cu.usbmodemXXXXX".
usb_address = '/dev/cu.usbmodem2144101'


def validate_result(result: bool):
    if result:
        print(f"Execution was successful.")
    else:
        print("Execution failed.")


def main():
    # Start the communication
    isot = isotope.Isotope(usb_address, DEBUG_ENABLED, response_timeout=5)
    isot.connect()

    print("Enable all PWM output ports")
    result = isot.pwms.enable()
    validate_result(result)

    print(f"PWM output ports are {'' if isot.pwms.is_enabled() else 'not'} enabled.")
    
    print(f"{len(isot.pwms)} PWM output ports available.")
    
    # Enumerate through all PWM output ports and set and get PWM values
    for i, port in enumerate(isot.pwms):
        print(f"Setting Port {i} PWM to 512")
        result = port.set_pwm(512)
        validate_result(result)

        actual_pwm = port.get_pwm()
        print(f"Actual PWM on the Isotope Board is {actual_pwm}")

    print("Disable all PWM output ports")
    result = isot.pwms.disable()
    validate_result(result)

    print(f"PWM output ports are {'' if isot.pwms.is_enabled() else 'not'} enabled.")

    # Close the connection
    isot.disconnect()


if __name__ == "__main__":
    main()
