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


def main():
    # Start the communication
    isot = isotope.Isotope(
        usb_address, DEBUG_ENABLED, response_timeout=5)
    isot.connect()

    # Enable the PWM output port
    if isot.pwms.enable():
        print("PWM output port enabled")
    else:
        raise Exception("Failed to enable the PWM output port")
    time.sleep(1)
    
    # Set and get the PWM output port value
    for i in range(0, 1024, 128):
        if not isot.pwms[port_id].set_pwm(i):
            raise Exception("Failed to set the PWM output port")
        time.sleep(0.5)
        if isot.pwms[port_id].get_pwm() != i:
            raise Exception("PWM output port value not set correctly")

    # Disable the PWM output port
    if isot.pwms.disable():
        print("PWM output port disabled")
    else:
        raise Exception("Failed to disable the PWM output port")

    # Close the connection
    isot.disconnect()


if __name__ == "__main__":
    main()
