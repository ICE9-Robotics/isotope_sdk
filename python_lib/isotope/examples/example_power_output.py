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


def main():
    # Start the communication
    isot = isotope.Isotope(
        usb_address, DEBUG_ENABLED, response_timeout=5)
    isot.connect()

    # Create a power output port object
    port = isot.powers[port_id]

    # Enable the power output port
    if port.enable():
        print("Power output port enabled")
    else:
        raise Exception("Failed to enable the power output port")
    time.sleep(1)

    # Disable the power output port
    if port.disable():
        print("Power output port disabled")
    else:
        raise Exception("Failed to disable the power output port")

    # Close the connection
    isot.disconnect()


if __name__ == "__main__":
    main()
