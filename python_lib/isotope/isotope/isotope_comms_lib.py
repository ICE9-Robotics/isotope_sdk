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
    SEC_PWM_MODE # used with "GET" and "SET" to set the PWM mode, i.e. using the standard PWM control or through the Servo library.
    SEC_ANALOG_INPUT # used with "GET" to read the analog input
    SEC_RGB_RED # used with "SET" to control the red channel of the RGB LED
    SEC_RGB_GREEN # used with "SET" to control the green channel of the RGB LED
    SEC_RGB_BLUE # used with "SET" to control the blue channel of the RGB LED
    SEC_MOTOR_STEP # used with "GET" and "SET" to set the number of steps to rotate the motor
    SEC_MOTOR_RPM_SPEED # used with "GET" and "SET" to set/read the motor speed in RPM
    SEC_MOTOR_STEP_ANGLE # used with "GET" to read the motor step angle
    SEC_MOTOR_CURRENT_MILLIAMP # used with "SET" to set the motor current in milliamps
    SEC_MOTOR_ENABLE # used with "SET" to enable or disable the motor
    
    # Response Definitions:
    RES_CMD_ACK # default response for successful commands
    RES_CMD_SUCCESS # response for successful commands
    RES_CMD_ABORT # response for aborted commands
    RES_ERR_GEN # general error response
    RES_ERR_WRONG_JSON_FORMAT # error response for wrong JSON format
    RES_ERR_WRONG_SEC_TYPE # error response for wrong command type
    RES_ERR_WRONG_SEC_SECTION # error response for unknown command section
    RES_ERR_WRONG_SEC_ITEM # error response for wrong command item (e.g. port number) for the section
    RES_ERR_WRONG_SEC_VALUE # error response for value out of range
    RES_ERR_HARDWARE_ERROR # error response for hardware error

    # Incoming Error Definitions:
    INC_ERR_NON_JSON_RESPONSE # error definition when non-JSON response is received
    INC_ERR_RESPONSE_TIMEOUT # error definition when response timeout

Examples
--------

    import isotope.isotope_comms_lib as icl
    
    icl_obj = icl.IsotopeCommsProtocol("COM3")
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
from threading import Thread
from enum import Enum

from isotope.isotope_exceptions import IsotopeCommsError

BOARD_NAME = "Isotope Board"

# Command type definitions
CMD_TYPE_GET = "GET"
CMD_TYPE_SET = "SET"

# Section Definitions
SEC_WHO_I_AM = "Who_I_am"
SEC_COMM_MAX_LATENCY = "Comm_max_latency"
SEC_ID_VALUE = "ID_value"
SEC_HEARTBEAT = "HeartBeat"
SEC_POWER_OUTPUT = "Power_output"
SEC_TEMP_SENSOR = "Temp_sensor"
SEC_PWM_OUTPUT = "PWM_output"
SEC_PWM_ENABLE = "PWM_enable"
SEC_PWM_MODE = "PWM_mode"
SEC_ANALOG_INPUT = "Analog_input"
SEC_RGB = "RGB"
SEC_MOTOR_STEP = "Motor_step"
SEC_MOTOR_RPM_SPEED = "Motor_rpm_speed"
SEC_MOTOR_CURRENT_MILLIAMP = "Motor_current_milliamps"
SEC_MOTOR_ENABLE = "Motor_enable"
SEC_MOTOR_STEP_ANGLE = "Motor_step_angle"

# Response Definitions
RES_CMD_ACK = "ACK"
RES_CMD_SUCCESS = "SUC"
RES_CMD_ABORT = "ABT"
RES_ERR_GEN = "ERR"
RES_ERR_WRONG_JSON_FORMAT = "ERR0"
RES_ERR_WRONG_SEC_TYPE = "ERR1"
RES_ERR_WRONG_SEC_SECTION = "ERR2"
RES_ERR_WRONG_SEC_ITEM = "ERR3"
RES_ERR_WRONG_SEC_VALUE = "ERR4"
RES_ERR_HARDWARE_ERROR = "ERR5"

INC_ERR_NON_JSON_RESPONSE = "ERRINC1"
INC_ERR_RESPONSE_TIMEOUT = "ERRINC2"

# Value defintions
PWM_MODE_STANDARD = 0
PWM_MODE_SERVO = 1
PWM_VALUE_TYPE_PWM = 0
PWM_VALUE_TYPE_MS = 1


class Response:
    """Response object for Isotope board communication.
    """

    def __init__(self, sequence: int = None, payload: str = None, error: str = None) -> None:
        """
        Args:
            sequence (int): Sequence number of the command.
            payload (str): Payload of the response.
            error (str): Error code of the response.
        """
        self.valid = sequence is not None
        self.sequence = sequence
        self.payload = payload
        self.error = error


class CmdResponseType(Enum):
    """Response type for the Isotope board.
    """
    Acknowledged = 1
    Succeeded = 2
    Aborted = 3
    Errored = 0


class IsotopeCommsProtocolBase:
    """Provides base methods for communicating with the Isotope board.

    This class provides base methods to communicate with the Isotope board using a serial connection.
    For implementation of the communication with different ports, please refer to the `isotope.port` module.

    See also
    --------
    isotope.port
    """

    def __init__(self, usb_address: str, response_timeout=5) -> None:
        """
        Args:
            usb_address (str): USB port address of the Isotope board.
            response_timeout (int): Time in seconds for waiting for responses from the Isotope board before timeout. Default is 5 seconds.
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
            if not self.ser.is_open:
                return
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

    def _send_cmd(self, sequence: int, type: str, section: str, item: int, value: int | list) -> str | tuple[str, str]:
        """Send command to the Isotope board.

        Args:
            sequence (int): Sequence number of the command.
            type (str): Type of the command, `CMD_TYPE_SET` or `CMD_TYPE_GET`.
            section (str): Section name, please refer to section definitions.
            item (int): Port ID.
            value (int | list): Value to be sent in a `CMD_TYPE_SET` command or discarded in a `CMD_TYPE_GET` command.

        Returns:
            None | str | tuple[str, str]: if `wait_for_answer` is True, returns None; otherwise, if `type` is `CMD_TYPE_SET`, returns message code; if `type` is `CMD_TYPE_GET`, returns payload and message code as a tuple.

        Raises:
            IsotopeCommsError: If the serial port is not open.
        """
        if self.ser is None:
            raise IsotopeCommsError("Serial port is not open.")

        if not isinstance(value, list):
            value = [value]
        message_s = json.dumps({"seq": sequence, "type": type, "section": section, "item": item, "value": value})
        while self._comms_busy:
            pass

        self._comms_busy = True
        try:
            self.ser.flush()
            self.ser.write(message_s.encode('ascii'))
        except Exception as e:
            self._comms_busy = False
            raise e
        self._comms_busy = False
        self.last_comm_tick = time.perf_counter()

        self._logger.debug(f"Outgoing >> {self.last_comm_tick:.6f} {message_s.strip()}")

    def _read_serial(self) -> str:
        """Get the reply from the Isotope board.

        Returns:
            str: Reply from the Isotope board.

        Raises:
            IsotopeCommsError: If the serial port is not open.
        """
        if self.ser is None:
            raise IsotopeCommsError("Serial port is not open.")
        while self._comms_busy:
            pass

        if self.ser.in_waiting > 0:
            self._comms_busy = True
            try:
                resp = self.ser.readline().decode('utf-8').strip()
            except Exception as e:
                self._comms_busy = False
                raise e
            self._comms_busy = False
            self._logger.debug(f"Incoming << {resp}")
        else:
            resp = ""
        return resp


class IsotopeCommsProtocol(IsotopeCommsProtocolBase):
    """Provides methods for communicating with the Isotope board, automatically handles sequence number, 
    and collects responses from the board.

    Note that maximum sequence number is 65535, after that it will reset to 0. This also means a maximum of 65535
    responses can be stored, after which oldest response will be overwritten.
    """

    def __init__(self, usb_address: str, response_timeout=5) -> None:
        """
        Args:
            usb_address (str): USB port address of the Isotope board.
            response_timeout (int): Time in seconds for waiting for responses from the Isotope board before timeout. Default is 5 seconds.
        """
        super().__init__(usb_address, response_timeout)
        self.sequence = 0  # Sequence number for the command
        self.responses: dict[int, Response] = {}  # Dictionary to store responses

        self.serial_reader_delay = 0.001
        self.serial_reader_thread = Thread(target=self._serial_reader_do_work)

    def connect(self) -> None:
        super().connect()
        try:
            self.serial_reader_thread.start()
        except:
            pass

    def disconnect(self) -> None:
        super().disconnect()
        try:
            self.serial_reader_thread.join()
        except:
            pass

    def send_cmd(self, type: str, section: str, item: int, value: int | list = 0, wait_for_answer: bool = True) -> int | Response | None:
        """Send command to the Isotope board.

        Args:
            type (str): Type of the command, `CMD_TYPE_SET` or `CMD_TYPE_GET`.
            section (str): Section name, please refer to section definitions.
            item (int): Port ID.
            value (int | list): Value to be sent in a `CMD_TYPE_SET` command or discarded in a `CMD_TYPE_GET` command.
            wait_for_answer (bool): If True, waits for the response from the board. Default is True.

        Returns:
            int | Response: if `wait_for_answer` is True, returns the sequence number; otherwise, if a response is received, 
                returns the response as a Response instance. If no response is received, returns None.
        """

        cmd_sequence = self.sequence
        self._send_cmd(cmd_sequence, type, section, item, value)
        self.sequence += 1
        if self.sequence > 65535:
            self.sequence = 0

        if not wait_for_answer:
            return cmd_sequence
        self._logger.debug(f"Waiting for response for sequence {cmd_sequence}")

        return self.wait_and_retrieve_response(cmd_sequence)

    def retrieve_response(self, seq: int) -> Response | None:
        """Retrieve the response from the Isotope board. The response is then removed from the internal storage.

        Args:
            seq (int): Sequence number of the command.

        Returns:
            Response | None: The response from the board as a Response instance. None if the response is not found.
        """
        if seq in self.responses:
            return self.responses.pop(seq)
        else:
            return None

    def wait_and_retrieve_response(self, sequence: int) -> Response | None:
        """Wait and retrieve the response from the Isotope board until timeout. If a response is successfully
        retrieved, it is then removed from the internal storage.

        Args:
            sequence (int): Sequence number of the command

        Returns:
            Response | None: The response from the board as a Response instance. None if timeout and no response is found.
        """
        time_started = time.perf_counter()
        while (time.perf_counter() - time_started) < self.resp_timeout:
            resp = self.retrieve_response(sequence)
            if resp is not None:
                return resp
            time.sleep(self.serial_reader_delay)
        return None

    def is_resp_ok(self, response: Response | None) -> CmdResponseType:
        """Check if the response is OK and logs error if not.

        Args:
            response (Response): Response from the Isotope board.

        Returns:
            int: 0 if the response is an error, 1 if the response is an ACK, 2 if the response is a SUCCESS.
        """
        if response is None:
            return CmdResponseType.Errored
        if response.error == RES_CMD_ACK:
            self._logger.debug("Responded ACK")
            return CmdResponseType.Acknowledged
        if response.error == RES_CMD_SUCCESS:
            self._logger.debug("Responded SUCCESS")
            return CmdResponseType.Succeeded
        if response.error == RES_CMD_ABORT:
            self._logger.debug("Responded ABORT")
            return CmdResponseType.Aborted
        else:
            self._log_error(response.error)
            return CmdResponseType.Errored

    def _serial_reader_do_work(self) -> None:
        """Thread worker for reading serial port.
        """
        last_read_time = 0
        while self.is_connected():
            while not self.ser.is_open:
                time.sleep(0.01)

            while time.perf_counter() - last_read_time < self.serial_reader_delay:
                time.sleep(self.serial_reader_delay/10)
            try:
                resp_s = self._read_serial()
            except:
                if self.ser.is_open:
                    continue
                else:
                    break
            last_read_time = time.perf_counter()
            resp = self._unpack_response(resp_s)

            if resp is not None:
                self.responses[resp.sequence] = resp

    def _unpack_response(self, resp: str) -> Response:
        """Unpack the response from the Isotope board.

        Args:
            resp (str): Response from the Isotope board.

        Returns:
            Response: The response from the board as a Response instance.
        """
        try:
            resp_dict = json.loads(resp)
            return Response(resp_dict['seq'], resp_dict['payload'], resp_dict['error'])
        except:
            return None

    def _log_error(self, error_code: str) -> None:
        """Log error message based on error code.

        Args:
            error_code (str): Error code from the response.
        """
        if error_code == RES_ERR_WRONG_JSON_FORMAT:
            msg = "Error Response from Isotope Board - Wrong JSON format string"
        elif error_code == RES_ERR_WRONG_SEC_TYPE:
            msg = "Error Response from Isotope Board - Wrong command Type"
        elif error_code == RES_ERR_WRONG_SEC_SECTION:
            msg = "Error Response from Isotope Board - Unknown command Section"
        elif error_code == RES_ERR_WRONG_SEC_ITEM:
            msg = "Error Response from Isotope Board - Wrong command Item (port number) for the Section"
        elif error_code == RES_ERR_WRONG_SEC_VALUE:
            msg = "Error Response from Isotope Board - Value out of range"
        elif error_code == INC_ERR_NON_JSON_RESPONSE:
            msg = "Incoming message error - Response is not a valid JSON format"
        elif error_code == INC_ERR_RESPONSE_TIMEOUT:
            msg = "Incoming message error - Timeout when waiting for serial response"
        elif error_code == RES_ERR_HARDWARE_ERROR:
            msg = "Error Response from Isotope Board - Hardware error"
        else:
            msg = "Error Response from Isotope Board - Unknown error code"
        self._logger.error(msg)
