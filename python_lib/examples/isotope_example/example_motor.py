import isotope
import time

DEBUG_ENABLED = True

# MOT port ID that the motor is connected to
port_id = 1

# PM35S-N48 motor specs:
# Step resolution: 7.5 degrees
# Rated current: 500 mA (set to 80%, i.e. 400 mA to avoid overheating)
resolution = 7.5
current = 400
rpm = 50

# USB address of the Isotope board. 
# For windows machine, this is usually "COMX" where X is the port number; 
# for Ubuntu, this is usually "/dev/ttyACMX", where X is the port number; 
# and for MacOS, this is usually "/dev/cu.usbmodemXXXXX".
usb_address = '/dev/cu.usbmodem21201'

def start_comms():
    icl = isotope.Isotope_comms_protocol(
        usb_address, DEBUG_ENABLED, response_timeout=5)
    if (not icl.verify_firmware()):
        raise Exception("Error: Could not connect to Isotope or firmware version is not compatible")
    return icl
   
def main():
    # Start the communication
    icl = start_comms()
    
    # Create a motor object 
    motor = isotope.port.Motor(icl, port_id, resolution, current, rpm)

    # Enable the motor port
    if motor.enable():
        print("Motor port enabled")
    else:
        raise Exception("Failed to enable the motor port")

    # Rotate the motor by steps
    if motor.rotate_by_steps(100):
        print("Motor roated by steps")
    else:
        raise Exception("Failed to rotate the motor by steps")
    time.sleep(1)

    # Rotate the motor by degrees
    if motor.rotate_by_degrees(90):
        print("Motor roated by degrees")
    else:
        raise Exception("Failed to rotate the motor by degrees")

    # Disable the motor port
    if motor.disable():
        print("Motor port disabled")
    else:
        raise Exception("Failed to disable the motor port")
    
    # Close the connection
    icl.close()

if __name__ == "__main__":
    main()