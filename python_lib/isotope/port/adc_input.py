from typing import Union
import isotope.isotope_comms_lib as icl
from .isotope_port import IsotopePort


class ADCInputPort(IsotopePort):
    """The ADCInputPort class is used to read inputs from the ADC ports, i.e. ADC 0, 1 and 2, on the Isotope board.

    Args:
        IsotopePort (_type_): _description_
    """

    def __init__(self, comms: icl.Isotope_comms_protocol, port_id: int) -> None:
        """Constructor for the ADCInputPort class. 

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

    def get_value(self) -> Union[int, None]:
        """Get the input value of the ADC port.

        Returns:
            int | None: The input value of the ADC port, or None if the read failed.
        """
        value, msg = self._comms.send_cmd(icl.CMD_TYPE_GET, icl.SEC_ANALOG_INPUT, self._id, 0)
        return value if self._comms.is_resp_ok(msg) else None


class ADCInput:
    """The ADCInput class is a list-like container for ADCInputPort objects representing all the ADC ports on the Isotope board.
    """

    def __init__(self, comms: icl.Isotope_comms_protocol) -> None:
        """Constructor for the ADCInput class. This class

        Args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class 
                that is used to communicate with the Isotope board.
        """
        self._ports = [ADCInputPort(comms, i) for i in range(3)]

    def __getitem__(self, key: int) -> ADCInputPort:
        """Get the ADC input port by index.

        Args:
            key (int): The index of the ADC input port.

        Returns:
            ADCInputPort: The ADC input port.
        """
        if key < 0 or key > 2:
            raise ValueError("Invalid port ID. Valid values are 0, 1 and 2.")
        return self._ports[key]
