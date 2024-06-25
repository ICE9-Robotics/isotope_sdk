import isotope

DEBUG_ENABLED = True

# USB address of the Isotope board.
# For windows machine, this is usually "COMX" where X is the port number;
# for Ubuntu, this is usually "/dev/ttyACMX", where X is the port number;
# and for MacOS, this is usually "/dev/cu.usbmodemXXXXX".
usb_address = '/dev/cu.usbmodem2144101'


def main():
    # Start the communication
    isot = isotope.Isotope(usb_address, DEBUG_ENABLED, response_timeout=5)
    isot.connect()
    
    print(f"{len(isot.temps)} TEMP ports available.")
    
    # Enumerate through all TEMP ports and get their values
    for i, temp in enumerate(isot.temps):
        print(f"TEMP port {i} value: {temp.get_value()}")

    # Close the connection
    isot.disconnect()


if __name__ == "__main__":
    main()
