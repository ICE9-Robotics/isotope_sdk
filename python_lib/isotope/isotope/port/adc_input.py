"""Contains `ADCInputPort` and `ADCInput` classes, used to hanlde the communication with the MOT ports on the Isotope board.

`ADCInputPort` class inherits from the `isotope.port.isotope_port.IsotopePort` class as the actual implementation of the communicaiton protocol 
while the `ADCInput` class inherits from the `isotope.port.isotope_port.IsotopePortContainer` class as a list-like container that holds `ADCInputPort` 
instances for all available ADC ports on the Isotope board.

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


class ADCInputPort(IsotopePort):
    """The ADCInputPort class is used to read inputs from the ADC ports, i.e. ADC 0, 1 and 2, on the Isotope board.
    """

    def __init__(self, comms: icl.Isotope_comms_protocol, port_id: int) -> None:
        """
        Args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class 
                that is used to communicate with the Isotope board.
            port_id (int): ID of the ADC port on the Isotope board. Valid values are 0, 1 and 2.

        Raises:
            ValueError: Invalid port ID. Valid values are 0, 1 and 2.
        """

        if port_id < 0 or port_id > 2:
            raise ValueError("Invalid port ID. Valid values are 0, 1 and 2.")

        super().__init__(comms, port_id)

    def get_value(self) -> int | None:
        """Get the input value of the ADC port.

        Returns:
            int | None: The input value of the ADC port, or None if the read failed.
        """
        self._logger.debug(f"Reading value from ADC port {self._id}...")
        value, msg = self._comms.send_cmd(icl.CMD_TYPE_GET, icl.SEC_ANALOG_INPUT, self._id, 0)
        return value if self._comms.is_resp_ok(msg) else None


class ADCInput(IsotopePortContainer[ADCInputPort]):
    """The ADCInput class is a list-like container for ADCInputPort objects representing all the ADC ports on the Isotope board.
    """

    def __init__(self, comms: icl.Isotope_comms_protocol) -> None:
        """
        Args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class 
                that is used to communicate with the Isotope board.
        """
        super().__init__(comms, 3)
        self._ports = [ADCInputPort(comms, i) for i in range(self._max_ports)]
