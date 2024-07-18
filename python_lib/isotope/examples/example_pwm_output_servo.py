# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!  WARNING  AVERTISSEMENT  警告  предупреждение  !!
# !!       Potential DAMAGE to your equipment      !!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Before running this script, make sure that servos connected to any
# PWM port can handle the angles 90 and 180.


import isotope
import time


DEBUG_ENABLED = False

# PWM output port ID to be controlled
port_id = 1

# USB address of the Isotope board.
# For windows machine, this is usually "COMX" where X is the port number;
# for Ubuntu, this is usually "/dev/ttyACMX", where X is the port number;
# and for MacOS, this is usually "/dev/cu.usbmodemXXXXX".
usb_address = '/dev/cu.usbmodem2144101'


def validate_result(result: bool):
    if result:
        print(f"Execution was successful.")
    else:
        print("Execution failed.")


def main():
    # Start the communication
    isot = isotope.Isotope(usb_address, DEBUG_ENABLED, response_timeout=5)
    isot.connect()

    print("Enable all PWM output ports")
    result = isot.pwms.enable()
    validate_result(result)

    print(f"PWM output ports are {'enabled' if isot.pwms.is_enabled() else 'disabled'}.")

    print(f"{len(isot.pwms)} PWM output ports available.")

    # Enumerate through all PWM output ports and set and get servo values
    for port in isot.pwms:
        print(f"=====Testing PWM Output Port {port.id}====")
        print(f"Setting Port {port.id} to servo mode.")
        result = port.set_servo_mode()
        validate_result(result)
        print(f"Setting Port {port.id} servo angle to 90")
        result = port.set_pwm(0)
        validate_result(result)
        time.sleep(1)
        print(f"Setting Port {port.id} servo angle to 180")
        result = port.set_pwm(180)
        validate_result(result)
        time.sleep(1)
        print(f"Setting Port {port.id} MS control value to 1500")
        result = port.set_ms(1500)
        validate_result(result)

    print("Disable all PWM output ports")
    result = isot.pwms.disable()
    validate_result(result)

    print(f"PWM output ports are {'enabled' if isot.pwms.is_enabled() else 'disabled'}.")

    # Close the connection
    isot.disconnect()


if __name__ == "__main__":
    main()
