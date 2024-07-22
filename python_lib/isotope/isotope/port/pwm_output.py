"""Contains `PWMOutputPort` and `PWMOutput` classes, used to handle the communication with 
the PWM ports on the Isotope board.

`PWMOutputPort` class inherits from the `isotope.port.isotope_port.IsotopePort` class as the actual implementation of the communicaiton protocol 
while the `PWMOutput` class inherits from the `isotope.port.isotope_port.IsotopePortContainer` class as a list-like container that holds `PWMOutputPort` 
instances for all available PWM ports on the Isotope board.

Notes
-----
Users are encouraged to use the isotope.Isotope class to access the ports instead of creating their own instances of these 
class directly.

Example
-------
    import isotope

    usb_address = 'COM3'
    port_id = 0
    
    # Start the communication
    isot = isotope.Isotope(usb_address)
    isot.connect()

    # Enable all PWM output ports
    result = isot.pwms.enable()

    if not result or not isot.pwms.is_enabled():
        raise Exception("Failed to enable PWM output ports.")
    
    # Get PWM output port at port_id
    port = isot.pwms[port_id]
    
    # Set PWM value of the PWM port to 512
    port.set_pwm(512)
    
    # Read the PWM value of the PWM port
    actual_pwm = port.get_control_value()
    print(f"Actual PWM on the Isotope Board is {actual_pwm}")

    # Disable all PWM output ports
    isot.pwms.disable()

    # Close the connection
    isot.disconnect()


See Also
--------
isotope.isotope
"""

import logging
import isotope.isotope_comms_lib as icl
from .isotope_port import IsotopePort, IsotopePortContainer


class PWMOutputPort(IsotopePort):
    """The PWMOutputPort class is used to control the PWM ports, i.e. PWM 0, 1, 2 and 3, on the Isotope board.
    """

    MODE_STANDARD = 0
    MODE_SERVO = 1

    def __init__(self, comms: icl.IsotopeCommsProtocol, port_id: int) -> None:
        """
        Args:
            comms (isotope_comms_lib.IsotopeCommsProtocol): The instance of the IsotopeCommsProtocol class that is used to communicate with the Isotope board.
            port_id (int): ID of the PWM output port on the Isotope board. Valid values are 0, 1, 2 and 3.

        Raises:
            ValueError: Invalid port ID. Valid values are 0, 1, 2 and 3.
        """

        if port_id < 0 or port_id > 3:
            raise ValueError("Invalid port ID. Valid values are 0, 1, 2 and 3.")

        super().__init__(comms, port_id)

    def set_standard_mode(self) -> bool:
        """Set the PWM port to standard mode.

        Returns:
            bool: True if the mode was successfully set, False otherwise.
        """
        return self._set_mode(PWMOutputPort.MODE_STANDARD)

    def set_servo_mode(self) -> bool:
        """Set the PWM port to servo mode.

        Returns:
            bool: True if the mode was successfully set, False otherwise.
        """
        return self._set_mode(PWMOutputPort.MODE_SERVO)

    def set_pwm(self, value: int) -> bool:
        """Set the PWM value of the PWM port.

        Args:
            value (int): The PWM value to set. Valid values are 0 to 1024.

        Returns:
            bool: True if the PWM value was successfully set, False otherwise.

        Raises:
            ValueError: PWM value must be between 0 and 1024.
        """
        self._logger.debug(f"Setting standard PWM value of PWM port {self._id} to {value}...")
        if value < 0 or value > 1024:
            raise ValueError("PWM value must be between 0 and 1024.")

        resp = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_PWM_OUTPUT, self._id, [value, icl.PWM_VALUE_TYPE_PWM])
        return self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded

    def set_ms(self, value: int) -> bool:
        """Set the PWM value of the PWM port in milliseconds.

        Args:
            value (int): The PWM value to set in milliseconds. Valid values are 0 to 20.

        Returns:
            bool: True if the PWM value was successfully set, False otherwise.

        Raises:
            ValueError: PWM value must be between 0 and 20.
        """
        self._logger.debug(f"Setting microsecond value of PWM port {self._id} to {value}...")

        resp = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_PWM_OUTPUT, self._id, [value, icl.PWM_VALUE_TYPE_MS])
        return self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded

    def get_control_value(self) -> int | None:
        """Read the control value last sent to the PWM port.

        Returns:
            int | None: The control value of the PWM port, or None if the read failed.
        """
        self._logger.debug(f"Reading control value from PWM port {self._id}...")
        resp = self._comms.send_cmd(icl.CMD_TYPE_GET, icl.SEC_PWM_OUTPUT, self._id, 0)
        return int(resp.payload) if self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded else None

    def _set_mode(self, mode: int) -> bool:
        """Set the mode of the PWM port.

        Args:
            mode (int): The mode to set. Valid values are 0 (standard) and 1 (servo).

        Raises:
            ValueError: Mode value must be 0 or 1.

        Returns:
            bool: True if the mode was successfully set, False otherwise.
        """
        self._logger.debug(f"Setting mode of PWM port {self._id} to {mode}...")
        if mode != icl.PWM_MODE_STANDARD and mode != icl.PWM_MODE_SERVO:
            raise ValueError("Mode value must be 0 or 1.")
        resp = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_PWM_MODE, self._id, mode)
        return self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded


class PWMOutput(IsotopePortContainer[PWMOutputPort]):
    """The PWMOutput class is a list-like container for PWMOutputPort objects representing all the PWM output ports on the Isotope board.
    """

    def __init__(self, comms: icl.IsotopeCommsProtocol) -> None:
        """
        Args:
            comms (isotope_comms_lib.IsotopeCommsProtocol): The instance of the IsotopeCommsProtocol class 
                that is used to communicate with the Isotope board.
        """
        self._logger = logging.getLogger(__package__)
        super().__init__(comms, 4)
        self._ports = [PWMOutputPort(comms, i) for i in range(self._max_port_count)]

    def enable(self) -> bool:
        """Enable all PWM outputs.

        Returns:
            bool: True if successful, False otherwise.
        """
        self._logger.debug("Enabling PWM outputs...")
        resp = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_PWM_ENABLE, 0, 1)
        return self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded

    def disable(self) -> bool:
        """Disable all PWM outputs.

        Returns:
            bool: True if successful, False otherwise.
        """
        self._logger.debug("Disabling PWM outputs...")
        resp = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_PWM_ENABLE, 0, 0)
        return self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded

    def is_enabled(self) -> bool:
        """Check if PWM outputs are enabled.

        Returns:
            bool: True if enabled, False otherwise.
        """
        self._logger.debug("Checking if PWM outputs are enabled...")
        resp = self._comms.send_cmd(icl.CMD_TYPE_GET, icl.SEC_PWM_ENABLE, 0, 0)
        return self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded and int(resp.payload) == 1
