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


def start_comms():
    icl = isotope.Isotope_comms_protocol(
        usb_address, DEBUG_ENABLED, response_timeout=5)
    if (not icl.verify_firmware()):
        raise Exception(
            "Error: Could not connect to Isotope or firmware version is not compatible")
    return icl


def main():
    # Start the communication
    icl = start_comms()

    # Create a power output port object
    port = isotope.port.PowerOutput(icl, port_id)

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
    icl.close()


if __name__ == "__main__":
    main()
