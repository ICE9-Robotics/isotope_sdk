import time
import isotope

DEBUG_ENABLED = False

# USB address of the Isotope board.
# For windows machine, this is usually "COMX" where X is the port number;
# for Ubuntu, this is usually "/dev/ttyACMX", where X is the port number;
# and for MacOS, this is usually "/dev/cu.usbmodemXXXXX".
usb_address = '/dev/cu.usbmodem2144101'


def main():
    def is_timeout():
        return time.perf_counter() - t_start > timeout
    
    # Start the communication
    isot = isotope.Isotope(usb_address, DEBUG_ENABLED, response_timeout=5)
    isot.connect()
    
    print(f"{len(isot.temps)} TEMP ports available.")
    
    # Enumerate through all TEMP ports to request a temperature reading
    for temp in isot.temps:
        print(f"Requesting temperature reading from port {temp.id}.")
        temp.request_reading()
        
    # Wait for the temperature readings to be available
    timeout = 1
    t_start = time.perf_counter()
    received = [False for _ in isot.temps]
    while sum(received) < len(isot.temps) and not is_timeout():
        for i, temp in enumerate(isot.temps):
            if received[i]:
                continue
            value = temp.retrieve_value()
            if value is None:
                continue
            received[i] = True
            print(f"TEMP port {temp.id} value: {value}")
    print(f"Temperature received from ports: {sum(received)}.")
    # Close the connection
    isot.disconnect()


if __name__ == "__main__":
    main()
