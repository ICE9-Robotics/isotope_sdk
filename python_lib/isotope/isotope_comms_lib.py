# /*
#   Isotope Breakout comms python implementation
#
#   Implementation of the comms protocol with the Isotope Breakout V0 board
#   Libary written to be used with Python 3.x
#
#   Example of how the JSON communication protocol looks:
#    {"type": "GET", "section": "Power_output", "item": 3, "value": 0}
#    Where 'type' can be 'GET' or 'SET', Get for retrieving values and SET for writting them
#    'Section' can be any of the sections defined under "Section Definitions"
#    'item' is a number in reference of which instance of motor controller or temp or etc
#    'value' is the value to be sent on a SET command. On a get command the value is discarded
#   Example of response from Breakout board:
#    {"payload": "180", "error": "ACK"}
#    Where payload is a string of the data requested. "error" is "ACK" when there are no errors,
#    And the rest of the errors are defined under Error Definitions
# */
# Imports------------------------------------------------------------------------
import serial
import time
import json
from typing import Union

minimum_firmware = (1, 0, 0)
BOARD_NAME = "Isotope Board"

# Command type definitions----------------------------------------------------------
CMD_TYPE_GET = "GET"
CMD_TYPE_SET = "SET"

# Section Definitions --------------------------------------------------------------
SEC_WHO_I_AM = "Who_I_am"
SEC_ID_VALUE = "ID_value"
SEC_POWER_OUTPUT = "Power_output"
SEC_TEMP_SENSOR = "Temp_sensor"
SEC_PWM_OUTPUT = "PWM_output"
SEC_PWM_ENABLE = "PWM_enable"
SEC_ANALOG_INPUT = "Analog_input"
SEC_RGB_RED = "RGB_red"
SEC_RGB_GREEN = "RGB_green"
SEC_RGB_BLUE = "RGB_blue"
SEC_MOTOR_STEP = "Motor_step"
SEC_MOTOR_RPM_SPEED = "Motor_rpm_speed"
SEC_MOTOR_CURRENT_MILLIAMP = "Motor_current_milliamps"
SEC_MOTOR_ENABLE = "Motor_enable"

# Response Definitions -------------------------------------------------------------
RES_ACK = "ACK"
RES_ERR_GEN = "ERR"
RES_ERR_WRONG_JSON_FORMAT = "ERR0"
RES_ERR_WRONG_SEC_TYPE = "ERR1"
RES_ERR_WRONG_SEC_SECTION = "ERR2"
RES_ERR_WRONG_SEC_ITEM = "ERR3"
RES_ERR_WRONG_SEC_VALUE = "ERR4"
RES_ERR_NON_JSON_RESPONSE = "ERR5"
RES_ERR_RESPONSE_TIMEOUT = "ERR6"


def firmware_from_string(firmware_string: str) -> tuple[int, ...]:
    """Converts firmware in string to int tuple.

    Args:
        firmware_string (str): firmware in string.

    Returns:
        tuple[int, ...]: firmware in tuple.
    """
    return tuple(map(int, firmware_string.split(".")))


def firmware_to_string(firmware_tuple: tuple[int, ...]) -> str:
    """Converts firmware in int tuple to string.

    Args:
        firmware_tuple (tuple[int, ...]): firmware to be converted.

    Returns:
        str: firmware in string.
    """
    return ".".join([str(i) for i in firmware_tuple])

class Isotope_comms_protocol:
    """Isotope_comms_protocol class for communication with the Isotope board.
    """

    def __init__(self, usb_address: str, debug=False, response_timeout=5) -> None:
        """Isotope_comms_protocol class for communication with the Isotope board.

        Args:
            usb_address (string): USB port address of the Isotope board. 
            debug (bool, optional): Set true to turn on debug information. Defaults to False.
            response_timeout (int, optional): Time in seconds for waiting for responses from the Isotope board before timeout. Defaults to 5 s.
        """
        self.usb_address = usb_address
        self.resp_timeout = response_timeout
        self.debug = debug
        self.serial_baudrate = 115200

        self.ser = serial.Serial(
            self.usb_address, self.serial_baudrate, timeout=0.5)  # open serial port
        
    def __del__(self) -> None:
        """Destructor to close the serial port.
        """
        try:
            self.close()
        except:
            pass
        
    def close(self) -> None:
        """Close the serial port.
        """
        self.ser.close()

    def verify_firmware(self) -> bool:
        """Verify the firmware version of the Isotope board.

        Returns:
            bool: True if the board is correct and firmware is supported. Otherwise, false.
        """
        payload, msg = self.send_cmd(CMD_TYPE_GET, SEC_WHO_I_AM, 0, 0)
        if not self._is_resp_ok(msg):
            return False
        if payload == "ISOTOPE_BOARD":
            if minimum_firmware != (0, 0, 0):
                print(
                    f"Requires minimum firmware v{firmware_to_string(minimum_firmware)}, board firmware is v0.")
                return False
            return True

        return self._confirm_firmware(payload)

    def set_pwm_value(self, item: int, pwm_val: int) -> bool:
        """Set PWM value for the specified port.

        Args:
            item (int): PWM port ID, ranging from 0 to 3.
            pwm_val (int): PWM value to be set, ranging from 0 to 1024.

        Returns:
            bool: True if successful. Otherwise, false.
        """
        msg = self.send_cmd(CMD_TYPE_SET, SEC_PWM_OUTPUT, item, pwm_val)
        return self._is_resp_ok(msg)

    def set_pwm_enable(self, enable_val: int) -> bool:
        """Set all PWM outputs enable or disable.

        Args:
            enable_val (int): 1 to enable and 0 to disable all PWM outputs.

        Returns:
            bool: True if successful. Otherwise, false.
        """
        msg = self.send_cmd(CMD_TYPE_SET, SEC_PWM_ENABLE, 0, enable_val)
        return self._is_resp_ok(msg)

    def set_power_output(self, item: int, pwm_val: int) -> bool:
        """Set PWM value for the specified power output port.

        Args:
            item (int): Output port ID, ranging from 0 to 2.
            pwm_val (int): PWM value, ranging from 0 to 1024.

        Returns:
            bool: True if successful. Otherwise, false.
        """
        msg = self.send_cmd(CMD_TYPE_SET, SEC_POWER_OUTPUT, item, pwm_val)
        return self._is_resp_ok(msg)

    def set_motor_rpm(self, item: int, rpm_val: int) -> bool:
        """Set motor command speed in RPM.

        Args:
            item (int): Motor ID, ranging from 0 to 3.
            rpm_val (int): Speed value in RPM.

        Returns:
            bool: True if successful. Otherwise, false.
        """
        msg = self.send_cmd(CMD_TYPE_SET, SEC_MOTOR_RPM_SPEED, item, rpm_val)
        return self._is_resp_ok(msg)

    def set_motor_step(self, item: int, step_val: int) -> bool:
        """Command motor to move specified number of steps.

        Args:
            item (int): Motor ID, ranging from 0 to 3.
            step_val (int): Number of steps to rotate.

        Returns:
            bool: True if successful. Otherwise, false.
        """
        msg = self.send_cmd(CMD_TYPE_SET, SEC_MOTOR_STEP, item, step_val)
        return self._is_resp_ok(msg)

    def set_motor_current_milliamps(self, item: int, current_val: int) -> bool:
        """Set current supplied to the motor.

        Args:
            item (int): Motor ID, ranging from 0 to 3.
            current_val (int): Value of current in milli amperes.

        Returns:
            bool: True if successful. Otherwise, false.
        """
        msg = self.send_cmd(
            CMD_TYPE_SET, SEC_MOTOR_CURRENT_MILLIAMP, item, current_val)
        return self._is_resp_ok(msg)

    def set_motor_enable(self, item: int, enable_val: bool) -> bool:
        """Toggle motor enable or disable state.

        Args:
            item (int): Motor ID, ranging from 0 to 3.
            enable_val (bool): 1 to enable and 0 to disable.

        Returns:
            bool: True if successful. Otherwise, false.
        """
        msg = self.send_cmd(CMD_TYPE_SET, SEC_MOTOR_ENABLE, item, enable_val)
        return self._is_resp_ok(msg)

    def set_RGB_colour(self, red_i: int, green_i: int, blue_i: int) -> bool:
        """Set RGB colour.

        Args:
            red_i (int): Value for the red channel, ranging from 0 to 255.
            green_i (int): Value for the green channel, ranging from 0 to 255.
            blue_i (int): Value for the blue channel, ranging from 0 to 255.

        Returns:
            bool: True if successful. Otherwise, false.
        """
        msg = self.send_cmd(CMD_TYPE_SET, SEC_RGB_RED, 0,
                            self.clamp_i(red_i, 0, 255))
        ok = self._is_resp_ok(msg)
        msg = self.send_cmd(CMD_TYPE_SET, SEC_RGB_GREEN, 0,
                            self.clamp_i(green_i, 0, 255))
        ok = ok and self._is_resp_ok(msg)
        msg = self.send_cmd(CMD_TYPE_SET, SEC_RGB_BLUE, 0,
                            self.clamp_i(blue_i, 0, 255))
        return ok and self._is_resp_ok(msg)

    # ---- Read Commands------------------

    def get_temp_sensor(self, item: int) -> int:
        """Get temperature value from the specified port.

        Args:
            item (int): Temperature port ID, ranging from 0 to 2.

        Returns:
            int: Temperature value.
        """
        temp_value, msg = self.send_cmd(CMD_TYPE_GET, SEC_TEMP_SENSOR, item, 0)
        if not self._is_resp_ok(msg):
            return False
        return float(temp_value)

    def get_pwm_value(self, item: int) -> int:
        """Get PWM value from the specified port.

        Args:
            item (int): PWM port ID, ranging from 0 to 3.

        Returns:
            int: PWM value.
        """
        pwm_value, msg = self.send_cmd(CMD_TYPE_GET, SEC_PWM_OUTPUT, item, 0)
        if not self._is_resp_ok(msg):
            return False
        return int(pwm_value)

    def get_pwm_enable(self) -> int:
        """Get PWM enabled or disabled state.

        Returns:
            int: 1 for enabled and 0 for disabled state.
        """
        pwm_enable, msg = self.send_cmd(CMD_TYPE_GET, SEC_PWM_ENABLE, 0, 0)
        if not self._is_resp_ok(msg):
            return False
        return int(pwm_enable)

    def get_power_output(self, item: int) -> int:
        """Get PWM value of the power output port.

        Args:
            item (int): Power output port ID, ranging from 0 to 2.

        Returns:
            int: PWM value.
        """
        pwm_value, msg = self.send_cmd(CMD_TYPE_GET, SEC_POWER_OUTPUT, item, 0)
        if not self._is_resp_ok(msg):
            return False
        return int(pwm_value)

    def get_analogue_input(self, item: int) -> int:
        """Get analogue input value from the specified ADC port.

        Args:
            item (int): ADC port ID, ranging from 0 to 2.

        Returns:
            int: Analogue value.
        """
        analogue_value, msg = self.send_cmd(
            CMD_TYPE_GET, SEC_ANALOG_INPUT, item, 0)
        if not self._is_resp_ok(msg):
            return False
        return int(analogue_value)

    def send_cmd(self, type: str, section: str, item: int, value: int) -> Union[str, tuple[str, str]]:
        """Send command to the Isotope board.

        Args:
            type (str): Type of the command, CMD_TYPE_SET or CMD_TYPE_GET.
            section (str): Section name, please refer to section definitions.
            item (int): Port ID.
            value (int): Value for the command.

        Returns:
            str | tuple[str, str]: for CMD_TYPE_SET, returns error/message code; for CMD_TYPE_GET, returns payload and error/message code as a tuple.
        """
        message_s = json.dumps(
            {"type": type, "section": section, "item": item, "value": value})
        self.ser.flush
        self.ser.write(message_s.encode('ascii'))

        self._debug("Outgoing >> ", message_s.strip())
        timeout_flag = self._wait_for_serial()
        if not timeout_flag:
            resp = self.ser.readline()
            self._debug("Incoming << ", resp.decode("utf-8").strip())
            try:
                resp_dict = json.loads(resp)
                error = resp_dict['error']
                payload = resp_dict['payload']
            except:
                error = RES_ERR_NON_JSON_RESPONSE
                payload = 0
        else:
            self._debug("Response timeout.")
            error = RES_ERR_RESPONSE_TIMEOUT
            payload = 0

        if type == CMD_TYPE_SET:
            return error
        else:
            return payload, error

    # Private functions------------------------------------------------------------

    def _print_error(self, error_code):
        if error_code == RES_ERR_WRONG_JSON_FORMAT:
            print("Error Response from Isotope Board - Wrong JSON format string")
        if error_code == RES_ERR_WRONG_SEC_TYPE:
            print("Error Response from Isotope Board - Wrong command Type")
        if error_code == RES_ERR_WRONG_SEC_SECTION:
            print("Error Response from Isotope Board - Unknown command Section")
        if error_code == RES_ERR_WRONG_SEC_ITEM:
            print(
                "Error Response from Isotope Board - Wrong command Item for the Section")
        if error_code == RES_ERR_WRONG_SEC_VALUE:
            print("Error Response from Isotope Board - Value out of range")
        if error_code == RES_ERR_NON_JSON_RESPONSE:
            print("Error Response from Isotope Board - Returned value cannot be parsed")
        if error_code == RES_ERR_RESPONSE_TIMEOUT:
            print("Error Response from Isotope Board - Waiting for response Timeout")

    def _confirm_firmware(self, payload):
        re = payload.split(",")
        assert (len(re) == 2)

        my_board_name = re[0].split("=")[1]
        if my_board_name != BOARD_NAME:
            self._debug("Error! No Isotpe found")
            return False
        self._debug("Found Isotope board!")

        my_firmware = re[1].split("=")[1]
        if firmware_from_string(my_firmware) >= minimum_firmware:
            self._debug(
                f"Verified! Board firmware: {my_firmware} > required minimum firmware.")
            return True
        else:
            print(
                f"Requires minimum firmware v{firmware_to_string(minimum_firmware)}, board firmware is v{my_firmware}.")
            return False

    def _is_resp_ok(self, msg):
        if (msg == RES_ACK):
            return True
        else:
            self._print_error(msg)
            return False

    def _wait_for_serial(self):
        time_started = time.perf_counter()
        while (time.perf_counter() - time_started) < self.resp_timeout:
            if (self.ser.in_waiting > 0):
                return False
        return True

    def _debug(self, *args, **kwargs):
        if self.debug:
            return print("[DEBUG]:", *args, **kwargs)

    # Static functions------------------------------------------------------------

    @staticmethod
    def clamp_i(i, min_i, max_i):
        """Clamp the value of i between min_i and max_i.

        Args:
            i (_type_): Value to be clamped.
            min_i (_type_): Nin value.
            max_i (_type_): Max value.

        Returns:
            _type_: Clamped value.
        """
        if i < min_i:
            return min_i
        elif i > max_i:
            return max_i
        else:
            return i
