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
import logging

BOARD_NAME = "Isotope Board"

# Command type definitions----------------------------------------------------------
CMD_TYPE_GET = "GET"
CMD_TYPE_SET = "SET"

# Section Definitions --------------------------------------------------------------
SEC_WHO_I_AM = "Who_I_am"
SEC_ID_VALUE = "ID_value"
SEC_HEARTBEAT = "Heartbeat"
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

INC_ERR_NON_JSON_RESPONSE = "ERRINC1"
INC_ERR_RESPONSE_TIMEOUT = "ERRINC2"


class IsotopeCommsError(Exception):
    """IsotopeCommsError class for exceptions related to the Isotope communication protocol.
    """
    pass

class Isotope_comms_protocol:
    """Isotope_comms_protocol class for communication with the Isotope board.
    This class provides methods to communicate with the Isotope board using a serial connection.
    """

    def __init__(self, usb_address: str, response_timeout=5) -> None:
        """Isotope_comms_protocol class for communication with the Isotope board.

        Args:
            usb_address (str): USB port address of the Isotope board.
            response_timeout (int): Time in seconds for waiting for responses from the Isotope board before timeout. Default is 5 seconds.
            serial_baudrate (int): Baud rate for the serial connection. Default is 115200.
        """
        self._logger = logging.getLogger(__package__)
        self.usb_address = usb_address
        self.resp_timeout = response_timeout
        self.serial_baudrate = 115200
        
        self.ser = None
        self.last_comm_tick = None
        
    def __del__(self) -> None:
        """Destructor to close the serial port.
        """
        try:
            self.disconnect()
        except:
            pass
        
    def connect(self) -> None:
        """Connect to the Isotope board.
        """
        self._logger.debug(f"Connecting to {BOARD_NAME}...")
        self._logger.debug(f"USB address: {self.usb_address}")
        self._logger.debug(f"Baud rate: {self.serial_baudrate}")
        try:
            self.ser = serial.Serial(
                self.usb_address, self.serial_baudrate, timeout=0.5)  # open serial port
            self._logger.debug(f"{BOARD_NAME} connected.")
        except Exception as e:
            self.ser = None
            self._logger.error(f"Failed to connect to {BOARD_NAME}.", exc_info=True)
            raise e

        self.ser.flush()
        
    def disconnect(self) -> None:
        """Disconnect from the Isotope board.
        """
        try:
            self.ser.close()
            self._logger.debug(f"{BOARD_NAME} disconnected.")
        except:
            pass
        
    def is_connected(self) -> bool:
        """Check if the Isotope board is connected.

        Returns:
            bool: True if the Isotope board is connected, False otherwise.
        """
        if self.ser is None:
            return False
        return self.ser.is_open

    def send_cmd(self, type: str, section: str, item: int, value: int) -> Union[str, tuple[str, str]]:
        """Send command to the Isotope board.

        Args:
            type (str): Type of the command, CMD_TYPE_SET or CMD_TYPE_GET.
            section (str): Section name, please refer to section definitions.
            item (int): Port ID.
            value (int): Value for the command.

        Returns:
            str | tuple[str, str]: for CMD_TYPE_SET, returns message code; for CMD_TYPE_GET, returns payload and message code as a tuple.
        """
        if self.ser is None:
            raise IsotopeCommsError("Serial port is not open.")
        
        message_s = json.dumps(
            {"type": type, "section": section, "item": item, "value": value})
        self.ser.flush()
        self.ser.write(message_s.encode('ascii'))
        self.last_comm_tick = time.perf_counter()
        
        self._logger.debug(f"Outgoing >> {self.last_comm_tick:.6f}", message_s.strip())
        received = self._wait_for_serial()
        if received:
            resp = self.ser.readline()
            self._logger.debug("Incoming << ", resp.decode("utf-8").strip())
            try:
                resp_dict = json.loads(resp)
                error = resp_dict['error']
                payload = resp_dict['payload']
            except:
                error = INC_ERR_NON_JSON_RESPONSE
                payload = 0
        else:
            self._logger.error("Response timeout.")
            error = INC_ERR_RESPONSE_TIMEOUT
            payload = 0

        if type == CMD_TYPE_SET:
            return error
        else:
            return payload, error

    def is_resp_ok(self, msg: str) -> bool:
        """Check if the response is OK and logs error if not.
        
        Returns:
            bool: True if the response is OK, False otherwise.
        """
        if (msg == RES_ACK):
            self._logger.debug("Response OK")
            return True
        else:
            self._log_error(msg)
            return False

    def _wait_for_serial(self) -> bool:
        """Wait for serial response.

        Returns:
            bool: True if reresponse is received, False if response timeout.
        """
        time_started = time.perf_counter()
        while (time.perf_counter() - time_started) < self.resp_timeout:
            if (self.ser.in_waiting > 0):
                return True
        return False
        
    def _log_error(self, error_code: str) -> None:
        """Log error message based on error code.

        Args:
            error_code (str): Error code from the response.
        """
        if error_code == RES_ERR_WRONG_JSON_FORMAT:
            msg = "Error Response from Isotope Board - Wrong JSON format string"
        if error_code == RES_ERR_WRONG_SEC_TYPE:
            msg = "Error Response from Isotope Board - Wrong command Type"
        if error_code == RES_ERR_WRONG_SEC_SECTION:
            msg = "Error Response from Isotope Board - Unknown command Section"
        if error_code == RES_ERR_WRONG_SEC_ITEM:
            msg = "Error Response from Isotope Board - Wrong command Item for the Section"
        if error_code == RES_ERR_WRONG_SEC_VALUE:
            msg = "Error Response from Isotope Board - Value out of range"
        if error_code == INC_ERR_NON_JSON_RESPONSE:
            msg = "Incoming message error - Response is not a valid JSON format"
        if error_code == INC_ERR_RESPONSE_TIMEOUT:
            msg = "Incoming message error - Timeout when waiting for serial response"
        
        self._logger.error(msg)