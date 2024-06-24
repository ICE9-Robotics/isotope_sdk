"""Main module that provides the Isotope class for communicating with the Isotope Breakout board and its I/O ports.

This module collects all python implementation of the isotope communication protocol into one place. 
All I/O ports are available as class variables through the Isotope class.

Examples
--------

    import isotope
    
    isot = isotope.Isotope("COM3")
    isot.connect()
    
    # enable power output port 0
    isot.powers[0].enable()
    
    # set PWM value of PWM output port 0
    isot.pwms[0].set_pwm(512)
    
    # read value from ADC input port 0
    value = isot.adcs[0].get_value()
    
    # read value from temperature sensor port 0
    value = isot.temps[0].get_value()
    
    # configure motor port 0
    isot.motors[0].configure(resolution=7, current=100, rpm=100)
    
    # move motor port 0
    isot.motors[0].rotate_by_steps(100)
    
    isot.disconnect()
    
See Also
--------
isotope.isotope_comms_lib
isotope.port
"""

import threading
import time
import logging
from serial.serialutil import SerialException
from .__version__ import __version_info__, __minimum_firmware__
from .utils.logging import setup_logger
from . import port
from . import isotope_comms_lib as icl

        
def version_from_string(firmware_string: str) -> tuple[int, ...]:
    """Converts version in string to int tuple.

    Args:
        firmware_string (str): version in string.

    Returns:
        tuple[int, ...]: version in tuple.
    """
    return tuple(map(int, firmware_string.split(".")))


def version_to_string(firmware_tuple: tuple[int, ...]) -> str:
    """Converts version in int tuple to string.

    Args:
        firmware_tuple (tuple[int, ...]): version to be converted.

    Returns:
        str: version in string.
    """
    return ".".join([str(i) for i in firmware_tuple])


def clamp_i(i: int, min_i: int, max_i: int) -> int:
    """Clamp the value of i between min_i and max_i.

    Args:
        i (int): Value to be clamped.
        min_i (int): Nin value.
        max_i (int): Max value.

    Returns:
        int: Clamped value.
    """
    if i < min_i:
        return min_i
    elif i > max_i:
        return max_i
    else:
        return i


class IsotopeException(Exception):
    """General exception for Isotope class.
    """
    pass


class Isotope:
    """The Isotope class is the higher-level class for communicating with the Isotope Breakout,
    with a single method call connect() to connect to the board and initialise all the I/O ports.
    A heartbeat thread is incorporated to keep the connection alive.
    
    The I/O ports can be accessed using the the class variables including:
    
    - `powers` for power output ports, i.e. Output X.
    
    - `motors` for stepper motor ports, i.e. MOT X.
    
    - `adcs` for analogue-digital-converter ports, i.e. ADC X.
    
    - `pwms` for PWM output ports, i.e. PWM X.
    
    - `temps` for temperature sensor ports, i.e. TEMP X.
    
    Attributes:
        heart_beat_interval (int): Interval for the heartbeat thread.
    """
    
    heart_beat_interval: int = 0.1 # Interval for the heartbeat thread.
    powers: port.PowerOutput # Instance of the PowerOutput class, for controlling the power output ports.
    motors: port.Motor # Instance of the Motor class, for controlling the motor ports.
    adcs: port.ADCInput # Instance of the ADCInput class, for reading the ADC input ports.
    pwms: port.PWMOutput # Instance of the PWMOutput class, for controlling the PWM output ports.
    temps: port.TempInput # Instance of the TempInput class, for reading the temperature input ports.
    
    def __init__(self, usb_address: str, debug=False, response_timeout=5) -> None:
        """Constructor for the Isotope class.

        Args:
            usb_address (str): USB port address of the Isotope board.
            debug (bool): Set to True to enable debug information. Default is False.
            response_timeout (int): Time in seconds for waiting for responses from the Isotope board before timeout. Default is 5 seconds.
            serial_baudrate (int): Baud rate for the serial connection. Default is 115200.
        """
        screen_level = logging.DEBUG if debug else logging.INFO
        self._logger = setup_logger(__package__, screen_level=screen_level)
        self._logger.info("==============================================")
        self._logger.info(f"Initiating Isotope Breakout connected to port {usb_address}")
        self._logger.info(f"SDK version: {version_to_string(__version_info__)}")
        self._logger.info(f"Minimum firmware: {version_to_string(__minimum_firmware__)}")
        self._logger.info(f"Response timeout: {response_timeout}")
        
        self.comms = icl.Isotope_comms_protocol(usb_address, response_timeout)
        
        try:
            self.powers = port.PowerOutput(self.comms)
            self.motors = port.Motor(self.comms)
            self.adcs = port.ADCInput(self.comms)
            self.pwms = port.PWMOutput(self.comms)
            self.temps = port.TempInput(self.comms)
        except ValueError as e:
            self._logger.error(e, exc_info=True)
            raise e
        
        self._heartbeat_thread = threading.Thread(target=self._heartbeat)
    
    def connect(self) -> bool:
        """Connect to the Isotope board.
        
        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            self.comms.connect()
            self._verify_firmware()
        except IsotopeException as e:
            self._logger.error(e, exc_info=True)
            raise e
        self._logger.info(f"Board firmware: {version_to_string(self.board_firmware)}")
        if self.comms.is_connected():
            self._heartbeat_thread.start()
            self._logger.debug("Heartbeat thread started.")
        return True
    
    def disconnect(self) -> None:
        """Disconnect from the Isotope board."""
        self.comms.disconnect()
    
    def set_RGB_colour(self, red_i: int, green_i: int, blue_i: int) -> bool:
        """Set RGB colour.

        Args:
            red_i (int): Value for the red channel, ranging from 0 to 255.
            green_i (int): Value for the green channel, ranging from 0 to 255.
            blue_i (int): Value for the blue channel, ranging from 0 to 255.

        Returns:
            bool: True if successful. Otherwise, false.
        """
        msg = self.comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_RGB_RED, 0,
                            clamp_i(red_i, 0, 255))
        ok = self.comms.is_resp_ok(msg)
        msg = self.comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_RGB_GREEN, 0,
                            clamp_i(green_i, 0, 255))
        ok = ok and self.comms.is_resp_ok(msg)
        msg = self.comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_RGB_BLUE, 0,
                            clamp_i(blue_i, 0, 255))
        return ok and self.comms.is_resp_ok(msg)
        
    def _heartbeat(self) -> None:
        """Heartbeat thread to keep the connection alive.
        """
        while self.comms.is_connected():
            if time.perf_counter() - self.comms.last_comm_tick < self.heart_beat_interval:
                time.sleep(0.1)
                continue
            try:
                self.comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_HEARTBEAT, 0, 0)
            except SerialException as e:
                self._logger.error(e, exc_info=True)
                pass

    def _verify_firmware(self):
        """Verify the firmware version of the Isotope board.
        """
        payload, msg = self.comms.send_cmd(icl.CMD_TYPE_GET, icl.SEC_WHO_I_AM, 0, 0)
        if not self.comms.is_resp_ok(msg):
            raise IsotopeException("Error! No Isotope found.")
        if payload == "ISOTOPE_BOARD":
            self.board_firmware = (0, 0, 0)
            if __minimum_firmware__ != (0, 0, 0):
                raise IsotopeException(f"Requires minimum firmware v{version_to_string(__minimum_firmware__)}, board firmware is v0.")
            return
        
        re = payload.split(",")
        if not len(re) == 2:
            raise IsotopeException("Error! Wrong firmware format")

        my_board_name = re[0].split("=")[1]
        if my_board_name != icl.BOARD_NAME:
            raise IsotopeException("Error! No Isotpe found")
        self._logger.debug("Found Isotope board!")

        my_firmware = re[1].split("=")[1]
        self.board_firmware = version_from_string(my_firmware)
        if self.board_firmware >= __minimum_firmware__:
            return
        raise IsotopeException(f"Requires minimum firmware v{version_to_string(__minimum_firmware__)}, board firmware is v{my_firmware}.")