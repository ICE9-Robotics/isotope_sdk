import isotope
import time

DEBUG_ENABLED = False

# USB address of the Isotope board.
# For windows machine, this is usually "COMX" where X is the port number;
# for Ubuntu, this is usually "/dev/ttyACMX", where X is the port number;
# and for MacOS, this is usually "/dev/cu.usbmodemXXXXX".
usb_address = '/dev/cu.usbmodem2144101'


def validate_result(result: bool):
    if result:
        print("Execution was successful.")
    else:
        print("Execution failed.")


def main():
    # Start the communication
    isot = isotope.Isotope(usb_address, DEBUG_ENABLED, response_timeout=5)
    isot.connect()

    print(f"{len(isot.powers)} power output ports available.")

    for port in isot.powers:
        print(f"=====Testing Power Output Port {port.id}====")
        print(f"Enable Port {port.id} with default PWM: {port.default_pwm}.")
        result = port.enable()
        validate_result(result)
        
        if not result or not port.is_enabled():
            raise Exception("Failed to enable power output port.")
        
        print(f"Change Port {port.id} default PWM to 300")
        result = port.default_pwm = 300
        
        print(f"Update Port {port.id} to new default PWM")
        result = port.enable()
        validate_result(result)
        
        
        print(f"Change Port {port.id} to a custom PWM value of 512")
        result = port.enable(512)
        validate_result(result)
    
        print(f"Disable Port {port.id}")
        result = port.disable()
        validate_result(result)

    # Close the connection
    isot.disconnect()


if __name__ == "__main__":
    main()
