"""Contains `PWMOutputPort` and `PWMOutput` classes, used to hanlde the communication with 
the PWM ports on the Isotope board.

`PWMOutputPort` class inherits from the `isotope.port.isotope_port.IsotopePort` class as the actual implementation of the communicaiton protocol 
while the `PWMOutput` class inherits from the `isotope.port.isotope_port.IsotopePortContainer` class as a list-like container that holds `PWMOutputPort` 
instances for all available PWM ports on the Isotope board.

Notes
-----
Users are encouraged to use the Isotope class to access the ports instead of creating their own instances of these 
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
    actual_pwm = port.get_pwm()
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

    def __init__(self, comms: icl.Isotope_comms_protocol, port_id: int) -> None:
        """
        Args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class that is used to communicate with the Isotope board.
            port_id (int): ID of the PWM output port on the Isotope board. Valid values are 0, 1, 2 and 3.

        Raises:
            ValueError: Invalid port ID. Valid values are 0, 1, 2 and 3.
        """

        if port_id < 0 or port_id > 3:
            raise ValueError("Invalid port ID. Valid values are 0, 1, 2 and 3.")

        super().__init__(comms, port_id)

    def set_pwm(self, value: int) -> bool:
        """Set the PWM value of the PWM port.

        Args:
            value (int): The PWM value to set. Valid values are 0 to 1024.

        Returns:
            bool: True if the PWM value was successfully set, False otherwise.

        Raises:
            ValueError: PWM value must be between 0 and 1024.
        """
        self._logger.debug(f"Setting PWM value of PWM port {self._id} to {value}...")
        if value < 0 or value > 1024:
            raise ValueError("PWM value must be between 0 and 1024.")

        msg = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_PWM_OUTPUT, self._id, value)
        return self._comms.is_resp_ok(msg)

    def get_pwm(self) -> int | None:
        """Read the PWM value of the PWM port.

        Returns:
            int | None: The PWM value of the PWM port, or None if the read failed.
        """
        self._logger.debug(f"Reading PWM value from PWM port {self._id}...")
        value, msg = self._comms.send_cmd(icl.CMD_TYPE_GET, icl.SEC_PWM_OUTPUT, self._id, 0)
        return int(value) if self._comms.is_resp_ok(msg) else None


class PWMOutput(IsotopePortContainer[PWMOutputPort]):
    """The PWMOutput class is a list-like container for PWMOutputPort objects representing all the PWM output ports on the Isotope board.
    """

    def __init__(self, comms: icl.Isotope_comms_protocol) -> None:
        """
        Args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class 
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
        msg = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_PWM_ENABLE, 0, 1)
        return self._comms.is_resp_ok(msg)

    def disable(self) -> bool:
        """Disable all PWM outputs.

        Returns:
            bool: True if successful, False otherwise.
        """
        self._logger.debug("Disabling PWM outputs...")
        msg = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_PWM_ENABLE, 0, 0)
        return self._comms.is_resp_ok(msg)

    def is_enabled(self) -> bool:
        """Check if PWM outputs are enabled.

        Returns:
            bool: True if enabled, False otherwise.
        """
        self._logger.debug("Checking if PWM outputs are enabled...")
        val, msg = self._comms.send_cmd(icl.CMD_TYPE_GET, icl.SEC_PWM_ENABLE, 0, 0)
        return self._comms.is_resp_ok(msg) and int(val) == 1
