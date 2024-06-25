import isotope

DEBUG_ENABLED = True

# ADC input port ID to be controlled
port_id = 1

# USB address of the Isotope board.
# For windows machine, this is usually "COMX" where X is the port number;
# for Ubuntu, this is usually "/dev/ttyACMX", where X is the port number;
# and for MacOS, this is usually "/dev/cu.usbmodemXXXXX".
usb_address = '/dev/cu.usbmodem2144101'


def main():
    # Start the communication
    isot = isotope.Isotope(usb_address, DEBUG_ENABLED, response_timeout=5)
    isot.connect()
    
    print(f"{len(isot.adcs)} ADC ports available.")
    
    # Get the ADC port value
    for i, adc in enumerate(isot.adcs):
        print(f"ADC port {i} value: {adc.get_value()}")
        
    # Get the value of a specific ADC port
    value = isot.adcs[1].get_value()
    print(f"ADC port 1 value: {value}")

    # Close the connection
    isot.disconnect()


if __name__ == "__main__":
    main()
