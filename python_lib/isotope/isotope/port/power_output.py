"""Contains `PowerOutputPort` and `PowerOutput` classes, used to hanlde the communication with 
the Output ports on the Isotope board.

`PowerOutputPort` class inherits from the `isotope.port.isotope_port.IsotopePort` class as the actual implementation of the communicaiton protocol 
while the `PowerOutput` class inherits from the `isotope.port.isotope_port.IsotopePortContainer` class as a list-like container that holds `PowerOutputPort` 
instances for all available Output ports on the Isotope board.

Notes
-----
Users are encouraged to use the Isotope class to access the ports instead of creating their own instances of these 
class directly.

See Also
--------
isotope.isotope
"""

import isotope.isotope_comms_lib as icl
from .isotope_port import IsotopePort, IsotopePortContainer


class PowerOutputPort(IsotopePort):
    """The PowerOutputPort class is used to control the PWM enabled power output ports, i.e. Output 0, 1 and 2, on the Isotope board."""

    _defaut_pwm: int = 1024
    _current_pwm: int = 0

    def __init__(self, comms: icl.Isotope_comms_protocol, port_id: int) -> None:
        """
        Args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class that is used to communicate with the Isotope board.
            port_id (int): ID of the power output port on the Isotope board. Valid values are 0, 1 and 2.
            pwm_val (int): Sets the PWM control of the power output port. Valid values are 0 to 1024. Defaults to 1024.

        Raises:
            ValueError: Invalid port ID. Valid values are 0, 1 and 2.
        """

        if port_id < 0 or port_id > 2:
            raise ValueError("Invalid port ID. Valid values are 0, 1 and 2.")

        super().__init__(comms, port_id)

    @property
    def default_pwm(self) -> int:
        """Get the default PWM value of the power output port as set in the constructor.

        Returns:
            int: The default PWM value of the power output port.
        """
        return self._defaut_pwm

    @default_pwm.setter
    def default_pwm(self, value: int) -> None:
        """Set the default PWM value of the power output port.

        Args:
            value (int): The default PWM value to set. Valid values are 0 to 1024.

        Raises:
            ValueError: PWM value must be between 0 and 1024.
        """
        if value < 0 or value > 1024:
            raise ValueError("PWM value must be between 0 and 1024.")
        self._defaut_pwm = value

    def enable(self, pwm: int = None) -> bool:
        """Enable the power output ports. When this function is called, voltage will be applied cross the terminals of the 
            power output port. The current limit is configured by the PWM value. 

        pwm (int, optional): Sets the PWM control of the power output port. Valid values are 0 to 1024. Defaults to the default_pwm.
            Note that a value of 0 is equivalent to disabling the power output port by calling the disable() function.
            Setting the PWM value to 1024 to provide constant voltage.

        Returns:
            bool: True if the power output port was successfully enabled, False otherwise.

        Raises:
            ValueError: PWM value must be between 0 and 1024.
        """
        self._logger.debug(f"Enabling power output port {self._id} with PWM value of {pwm}...")
        if pwm is not None and (pwm < 0 or pwm > 1024):
            raise ValueError("PWM value must be between 0 and 1024.")
        if pwm == 0:
            return self.disable()
        if pwm is None:
            pwm = self._defaut_pwm
            self._logger.debug(f"Using default PWM value of {pwm}.")
        msg = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_POWER_OUTPUT, self._id, pwm)
        if self._comms.is_resp_ok(msg):
            self._current_pwm = pwm
            return True
        return False

    def disable(self) -> bool:
        """Disable the power output ports. When this function is called, the power output ports will be switched off.

        Returns:
            bool: True if the power output port was successfully disabled, False otherwise.
        """
        self._logger.debug(f"Disabling power output port {self._id}...")
        msg = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_POWER_OUTPUT, self._id, 0)
        if self._comms.is_resp_ok(msg):
            self._current_pwm = 0
            return True
        return False

    def is_enabled(self) -> bool:
        """Check if the power output port is enabled.

        Returns:
            bool: True if the power output port is enabled, False otherwise.
        """
        return self.get_pwm() > 0

    def get_pwm(self) -> int:
        """Get the current PWM value of the power output port.

        Returns:
            int: The current PWM value of the power output port.
        """
        # Potential vulnerability: The value of the PWM output port is not read from the Isotope board, but stored in the class instance.
        return self._current_pwm


class PowerOutput(IsotopePortContainer[PowerOutputPort]):
    """The PowerOutput class is a list-like container for PowerOutputPort objects representing all the power output ports on the Isotope board.
    """

    def __init__(self, comms: icl.Isotope_comms_protocol) -> None:
        """
        Args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class 
                that is used to communicate with the Isotope board.
        """
        super().__init__(comms, 3)
        self._ports = [PowerOutputPort(comms, i) for i in range(self._max_ports)]
