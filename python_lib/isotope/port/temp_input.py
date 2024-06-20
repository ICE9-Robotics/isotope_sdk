from typing import Union
import isotope.isotope_comms_lib as icl
from .isotope_port import IsotopePort, IsotopePortContainer


class TempInputPort(IsotopePort):
    """The TempInputPort class is used to read inputs from the temperature ports, i.e. TEMP 0, 1 and 2, on the Isotope board.
    """

    def __init__(self, comms: icl.Isotope_comms_protocol, port_id: int) -> None:
        """Constructor for the TempInputPort class. 

        Args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class 
                that is used to communicate with the Isotope board.
            port_id (int): ID of the temperature port on the Isotope board. Valid values are 0, 1 and 2.

        Raises:
            ValueError: Invalid port ID. Valid values are 0, 1 and 2.
        """

        if port_id < 0 or port_id > 2:
            raise ValueError("Invalid port ID. Valid values are 0, 1 and 2.")

        super().__init__(comms, port_id)

    def get_value(self) -> Union[int, None]:
        """Get the temperature input value from the temperature port.

        Returns:
            int | None: The temperature input value of the temperature port, or None if the read failed.
        """
        self._logger.debug(f"Reading value from temperature port {self._id}...")
        value, msg = self._comms.send_cmd(icl.CMD_TYPE_GET, icl.SEC_TEMP_SENSOR, self._id, 0)
        return value if self._comms.is_resp_ok(msg) else None


class TempInput(IsotopePortContainer[TempInputPort]):
    """The TempInput class is a list-like container for TempInputPort objects representing all the Temperature input ports on the Isotope board.
    """

    def __init__(self, comms: icl.Isotope_comms_protocol) -> None:
        """Constructor for the TempInput class.

        args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class 
                that is used to communicate with the Isotope board.
        """
        super().__init__(comms, 3)
        self._ports = [TempInputPort(comms, i) for i in range(self._max_ports)]
