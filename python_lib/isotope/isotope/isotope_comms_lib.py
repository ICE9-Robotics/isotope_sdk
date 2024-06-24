"""Base implementation of the Isotope Breakout board communication protocol.

This module is an implementation of the comms protocol with the Isotope Breakout board, 
which is a JSON-based protocol over a serial connection.

Notes
-----

An example of a JSON command send to the Isotope Breakout board:

    {
        "type": "GET", 
        "section": "Power_output", 
        "item": 3, 
        "value": 0
    }

Where:

- `type` can be `CMD_TYPE_GET` for retrieving values or `CMD_TYPE_SET` for writting values.

- `Section` can be any of the sections defined under "Section Definitions" in exported constants.

- `item` is a number in reference of which instance of motor controller or temp or etc.

- `value` is the value to be sent in a "SET" command. In a "GET" command the value is discarded.

An example of response from Breakout board:

    {
        "payload": "180", 
        "error": "ACK"
    }
 
Where:

- `payload` is a string of the data requested. 

- `error` can be `ACK` when there is no error, or an error code defined under "Response Definitions" in exported constants.

Exported constants
------------------

    BOARD_NAME # equals "Isotope Board"
    
    # Command type definitions:
    CMD_TYPE_GET # for getting values from the board
    CMD_TYPE_SET # for setting values on the board

    # Section Definitions:
    SEC_WHO_I_AM # used with "GET" returns the board name and firmware version
    SEC_ID_VALUE # used with "GET" returns the board ID, unused.
    SEC_HEARTBEAT # used with "SET" to keep the connection alive
    SEC_POWER_OUTPUT # used with "GET" and "SET" to control the power output
    SEC_TEMP_SENSOR # used with "GET" to read the temperature sensor
    SEC_PWM_OUTPUT # used with "GET" and "SET" to control the PWM output
    SEC_PWM_ENABLE # used with "GET" and "SET" to enable or disable the PWM output
    SEC_ANALOG_INPUT # used with "GET" to read the analog input
    SEC_RGB_RED # used with "SET" to control the red channel of the RGB LED
    SEC_RGB_GREEN # used with "SET" to control the green channel of the RGB LED
    SEC_RGB_BLUE # used with "SET" to control the blue channel of the RGB LED
    SEC_MOTOR_STEP # used with "GET" and "SET" to set the number of steps to rotate the motor
    SEC_MOTOR_RPM_SPEED # used with "GET" and "SET" to set/read the motor speed in RPM
    SEC_MOTOR_CURRENT_MILLIAMP # used with "SET" to set the motor current in milliamps
    SEC_MOTOR_ENABLE # used with "SET" to enable or disable the motor
    
    # Response Definitions:
    RES_ACK # default response for successful commands
    RES_ERR_GEN # general error response
    RES_ERR_WRONG_JSON_FORMAT # error response for wrong JSON format
    RES_ERR_WRONG_SEC_TYPE # error response for wrong command type
    RES_ERR_WRONG_SEC_SECTION # error response for unknown command section
    RES_ERR_WRONG_SEC_ITEM # error response for wrong command item for the section
    RES_ERR_WRONG_SEC_VALUE # error response for value out of range

    # Incoming Error Definitions:
    INC_ERR_NON_JSON_RESPONSE # error definition when non-JSON response is received
    INC_ERR_RESPONSE_TIMEOUT # error definition when response timeout

Examples
--------

    import isotope.isotope_comms_lib as icl
    
    icl_obj = icl.Isotope_comms_protocol("COM3")
    icl_obj.connect()
    
    payload, msg = icl_obj.send_cmd(icl.CMD_TYPE_GET, icl.SEC_WHO_I_AM, 0, 0)
    if icl_obj.is_resp_ok(msg):
        print(f"isotope says: {payload}")
        
    icl_obj.disconnect()

See also
--------
isotope.port
isoport.isotope
"""


import serial
import time
import json
import logging

BOARD_NAME = "Isotope Board"

# Command type definitions
CMD_TYPE_GET = "GET"
CMD_TYPE_SET = "SET"

# Section Definitions
SEC_WHO_I_AM = "Who_I_am"
SEC_ID_VALUE = "ID_value"
SEC_HEARTBEAT = "HeartBeat"
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

# Response Definitions
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
    """Exceptions related to the Isotope communication protocol.
    """
    pass


class Isotope_comms_protocol:
    """Handles base methods for communicating with the Isotope board.

    This class provides base methods to communicate with the Isotope board using a serial connection.
    For low-level communicaiton with the ports on the Isotope board, please refer to the isotope.port module.
    
    See also
    --------
    isotope.port
    """

    def __init__(self, usb_address: str, response_timeout=5) -> None:
        """
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
        self._comms_busy = False

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

    def send_cmd(self, type: str, section: str, item: int, value: int) -> str | tuple[str, str]:
        """Send command to the Isotope board.

        Args:
            type (str): Type of the command, `CMD_TYPE_SET` or `CMD_TYPE_GET`.
            section (str): Section name, please refer to section definitions.
            item (int): Port ID.
            value (int): Value to be sent in a `CMD_TYPE_SET` command or discarded in a `CMD_TYPE_GET` command.

        Returns:
            str | tuple[str, str]: for `CMD_TYPE_SET`, returns message code; for `CMD_TYPE_GET`, returns payload and message code as a tuple.
        """
        if self.ser is None:
            raise IsotopeCommsError("Serial port is not open.")

        message_s = json.dumps(
            {"type": type, "section": section, "item": item, "value": value})

        while self._comms_busy:
            pass

        self._comms_busy = True
        self.ser.flush()
        self.ser.write(message_s.encode('ascii'))
        self.last_comm_tick = time.perf_counter()

        self._logger.debug(f"Outgoing >> {self.last_comm_tick:.6f} {message_s.strip()}")
        received = self._wait_for_serial()
        if received:
            resp = self.ser.readline()
            self._comms_busy = False
            self._logger.debug(f"Incoming << {resp.decode('utf-8').strip()}")
            try:
                resp_dict = json.loads(resp)
                error = resp_dict['error']
                payload = resp_dict['payload']
            except:
                error = INC_ERR_NON_JSON_RESPONSE
                payload = 0
        else:
            self._comms_busy = False
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
