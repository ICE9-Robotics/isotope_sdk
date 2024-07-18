# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!  WARNING  AVERTISSEMENT  警告  предупреждение  !!
# !!       Potential DAMAGE to your equipment      !!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Before running this script, make sure you confirm the current
# value is correctly set to the operating current of the motor 
# Otherwise, the motor and the PCB may be damaged.


import isotope
import time
import random


DEBUG_ENABLED = True

# MOT port ID that the motor is connected to
port_id = 1

# PM35S-N48 motor specs:
# Step resolution: 7.5 degrees
# Rated current: 500 mA
resolution = 7.5
current = 500
rpm = 100

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

    print(f"{len(isot.motors)} motor ports available.")

    # Operating individual motor ports
    for motor in isot.motors:
        # Configure motor port
        print(f"=====Configure motor {motor.id}====")
        motor.configure(resolution, current, rpm)

        # Retrieve your settings
        print(f"Resolution: {motor.resolution}")
        print(f"Current: {motor.current}")
        print(f"RPM: {motor.rpm}")

        # Update individual settings if needed
        result = motor.set_current(current)
        result = result and motor.set_rpm(rpm)
        validate_result(result)

        # Enable the motor port
        result = motor.enable()

        if not result or not motor.is_enabled():
            raise Exception("Failed to enable motor port.")
        
        # Rotate the motor by 90 degrees
        print(f"====Rotating motor {motor.id} by 90 degrees====")
        result = motor.rotate_by_degrees(90)
        validate_result(result)
        motor.wait_until_motion_completed()

        time.sleep(1)

        # Rotate the motor by 100 steps
        print(f"=====Rotating motor {motor.id} by 100 steps====")
        result = motor.rotate_by_steps(100)
        validate_result(result)
        motor.wait_until_motion_completed()

        # Disable the motor port
        print(f"=====Disable motor {motor.id}====")
        result = motor.disable()
        validate_result(result)

        time.sleep(1)
        
    # Parallel operation
    print(f"=====Parallel operation====")
    for motor in isot.motors:
        motor.enable()
        steps = random.randint(100, 200)
        print(f"Rotating motor {motor.id} by {steps} steps.")
        motor.rotate_by_steps(steps)
    
    completed = [False for _ in isot.motors]
    while not all(completed):
        for i, motor in enumerate(isot.motors):
            if completed[i]:
                continue
            if motor.is_motion_completed():
                completed[i] = True
                print(f"Motor {motor.id} has completed.")
        
    # Close the connection
    isot.disconnect()


if __name__ == "__main__":
    main()
