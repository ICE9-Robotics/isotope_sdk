"""Contains `TempInputPort` and `TempInput` classes, used to handle the communication with 
the TEMP ports on the Isotope board.

`TempInputPort` class inherits from the `isotope.port.isotope_port.IsotopePort` class as the actual implementation of the communicaiton protocol 
while the `TempInput` class inherits from the `isotope.port.isotope_port.IsotopePortContainer` class as a list-like container that holds `TempInputPort` 
instances for all available TEMP ports on the Isotope board.

Notes
-----
Users are encouraged to use the isotope.Isotope class to access the ports instead of creating their own instances of these 
class directly.

Example
-------
    import isotope
    
    usb_address = 'COM3'


    # Start the communication
    isot = isotope.Isotope(usb_address)
    isot.connect()
    
    # Enumerate through all TEMP ports and get their values
    for i, temp in enumerate(isot.temps):
        print(f"TEMP port {i} value: {temp.get_value()}")

    # Close the connection
    isot.disconnect()


See Also
--------
isotope.isotope
"""

import time
import isotope.isotope_comms_lib as icl
from isotope.isotope_exceptions import InvalidOperationException
from .isotope_port import IsotopePort, IsotopePortContainer


class TempInputPort(IsotopePort):
    """The TempInputPort class is used to read inputs from the temperature ports, i.e. TEMP 0, 1 and 2, on the Isotope board.
    """

    def __init__(self, comms: icl.IsotopeCommsProtocol, port_id: int) -> None:
        """
        Args:
            comms (isotope_comms_lib.IsotopeCommsProtocol): The instance of the IsotopeCommsProtocol class 
                that is used to communicate with the Isotope board.
            port_id (int): ID of the temperature port on the Isotope board. Valid values are 0, 1 and 2.

        Raises:
            ValueError: Invalid port ID. Valid values are 0, 1 and 2.
        """

        if port_id < 0 or port_id > 2:
            raise ValueError("Invalid port ID. Valid values are 0, 1 and 2.")

        self._requested = False
        self._current_sequence = 0
        self.temperature_reading_timeout = 1
        
        super().__init__(comms, port_id)

    def retrieve_value(self) -> int | None:
        """Get the temperature input value from the temperature port.

        Returns:
            int | None: The temperature input value of the temperature port, or None if the read failed.
            
        Raises:
            InvalidOperationException: If the temperature value has not been requested. Use `TempInputPort.request_value()` to request the value.
        """
        if not self._requested:
            raise InvalidOperationException("Value not requested. Use `TempInputPort.request_value()` to request the value.")
        resp = self._comms.retrieve_response(self._current_sequence)
        if self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded:
            self._requested = False
            return resp.payload
        return None
    
    def wait_and_retrieve_value(self) -> int | None:
        """Wait until the temperature chip has read the value from the temperature port and retrieve the value.
        Note that reading temperature take a few milliseconds to complete.
        Default timeout is 1 second. Use `TempInputPort.temperature_reading_timeout` to change the timeout period.

        Returns:
            int | None: The temperature input value of the temperature port, or None if the read failed.
            
        Raises:
            TimeoutError: If the timeout period is exceeded while waiting for the value.
        """
        self._logger.debug(f"Waiting for value from temperature port {self._id}...")
        t = time.perf_counter()
        while time.perf_counter() - t < self.temperature_reading_timeout:
            val = self.retrieve_value()
            if val is not None:
                return val
        raise TimeoutError(f"Timeout waiting for value from temperature port {self._id}.")

    def request_reading(self) -> bool:
        """Request the temperature chip to read value from the temperature port.
        Note that reading temperature take a few milliseconds to complete.
        Use `TempInputPort.get_value()` to check if a value is ready and if so retrieve the value.

        Returns:
            bool: True if the request was successful, False otherwise.
        """
        self._logger.debug(f"Requesting value from temperature port {self._id}...")
        resp = self._comms.send_cmd(icl.CMD_TYPE_GET, icl.SEC_TEMP_SENSOR, self._id)
        if self._comms.is_resp_ok(resp) == icl.CmdResponseType.Acknowledged:
            self._requested = True
            self._current_sequence = resp.sequence
            return True
        return False


class TempInput(IsotopePortContainer[TempInputPort]):
    """The TempInput class is a list-like container for TempInputPort objects representing all the Temperature input ports on the Isotope board.
    """

    def __init__(self, comms: icl.IsotopeCommsProtocol) -> None:
        """
        Args:
            comms (isotope_comms_lib.IsotopeCommsProtocol): The instance of the IsotopeCommsProtocol class 
                that is used to communicate with the Isotope board.
        """
        super().__init__(comms, 3)
        self._ports = [TempInputPort(comms, i) for i in range(self._max_port_count)]
