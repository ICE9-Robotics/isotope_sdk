import isotope
import time

DEBUG_ENABLED = True

# Temperature input port ID to be controlled
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
    
    # Get the TEMP port value
    temp = isot.temps[port_id].get_value()
    print(f"TEMP port value: {temp}")

    # Close the connection
    isot.disconnect()


if __name__ == "__main__":
    main()
