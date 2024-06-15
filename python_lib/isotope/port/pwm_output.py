from typing import Union
import isotope.isotope_comms_lib as icl
from .isotope_port import IsotopePort


class PWMOutputPort(IsotopePort):
    """The PWMOutputPort class is used to control the PWM ports, i.e. PWM 0, 1, 2 and 3, on the Isotope board.
    """

    def __init__(self, comms: icl.Isotope_comms_protocol, port_id: int) -> None:
        """Constructor for the PWM class. 

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
        if value < 0 or value > 1024:
            raise ValueError("PWM value must be between 0 and 1024.")

        msg = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_PWM_OUTPUT, self._id, value)
        return self._comms.is_resp_ok(msg)

    def get_pwm(self) -> Union[int, None]:
        """Read the PWM value of the PWM port.

        Returns:
            int | None: The PWM value of the PWM port, or None if the read failed.
        """
        value, msg = self._comms.send_cmd(icl.CMD_TYPE_GET, icl.SEC_PWM_OUTPUT, self._id, 0)
        return value if self._comms.is_resp_ok(msg) else None


class PWMOutput:
    """The PWMOutput class is a list-like container for PWMOutputPort objects representing all the PWM output ports on the Isotope board.
    """

    def __init__(self, comms: icl.Isotope_comms_protocol) -> None:
        """Constructor for the PWMOutput class.

        args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class 
                that is used to communicate with the Isotope board.
        """
        self._comms = comms
        self._ports = [PWMOutputPort(comms, i) for i in range(4)]

    def __getitem__(self, key: int) -> PWMOutputPort:
        """Get the PWM output port by index.

        Args:
            key (int): The index of the PWM output port.

        Returns:
            PWMOutputPort: The PWM output port.
        """
        if key < 0 or key > 3:
            raise ValueError("Invalid port ID. Valid values are 0, 1, 2 and 3.")
        return self._ports[key]
    
    def enable(self) -> bool:
        """Enable all PWM outputs.

        Returns:
            bool: True if successful, False otherwise.
        """
        msg = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_PWM_ENABLE, 0, 1)
        return self._comms.is_resp_ok(msg)
    
    def disable(self) -> bool:
        """Disable all PWM outputs.

        Returns:
            bool: True if successful, False otherwise.
        """
        msg = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_PWM_ENABLE, 0, 0)
        return self._comms.is_resp_ok(msg)
    
    def is_enabled(self) -> bool:
        """Check if PWM outputs are enabled.

        Returns:
            bool: True if enabled, False otherwise.
        """
        val, msg = self._comms.send_cmd(icl.CMD_TYPE_GET, icl.SEC_PWM_ENABLE, 0, 0)
        return self._comms.is_resp_ok(msg) and int(val) == 1
