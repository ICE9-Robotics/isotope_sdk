import isotope
import time

DEBUG_ENABLED = True

# PWM output port ID to be controlled
port_id = 1

# USB address of the Isotope board.
# For windows machine, this is usually "COMX" where X is the port number;
# for Ubuntu, this is usually "/dev/ttyACMX", where X is the port number;
# and for MacOS, this is usually "/dev/cu.usbmodemXXXXX".
usb_address = '/dev/cu.usbmodem21201'


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
    
    # Set and get the PWM output port value
    for i in range(0, 1024, 128):
        print(f"Setting Port {port_id} PWM to {i}")
        result = isot.pwms[port_id].set_pwm(i)
        validate_result(result)
        time.sleep(0.1)

        actual_pwm = isot.pwms[port_id].get_pwm()
        print(f"Actual PWM on the Isotope Board is {actual_pwm}")

    print("Disable all PWM output ports")
    result = isot.pwms.disable():
    validate_result(result)

    print(f"PWM output ports are {'' if isot.pwms.is_enabled() else 'not'} enabled.")

    # Close the connection
    isot.disconnect()


if __name__ == "__main__":
    main()
