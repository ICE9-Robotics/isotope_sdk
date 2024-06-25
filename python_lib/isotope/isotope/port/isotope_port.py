"""Contains abstract classes for other submodules that hanldes the communication with specific I/O ports on the Isotope board.

`IsotopePort` class is the actual implementation of the communicaiton protocol while the `IsotopePortContainer` class is
a list-like container for `IsotopePort` objects representing all the corresponding ports on the Isotope board.

Notes for developers
--------------------
For each I/O port type on the Isotope board, a new module should be created in the `port` super-module. The module should 
contain two classes: one to inherit from `IsotopePort` and the other from `IsotopePortContainer`. Functions identical for all
ports of the same type should be implemented in the `IsotopePort` class, while the `IsotopePortContainer` class should be as
simple as possible and only contain the constructor in most cases to initialise the list of ports.

In some situation, taking the example of the `isotope.port.pwm_output.PWMOutput` class, the inheritance of the `IsotopePortContainer` class can 
contain additional functions that control the group of ports as a whole such as `isotope.port.pwm_output.PWMOutput.enable()` and 
`isotope.port.pwm_output.PWMOutput.disable()`.

See Also
--------
isotope.port.adc_input
isotope.port.motor
isotope.port.power_output
isotope.port.pwm_output
isotope.port.temp_input
"""

import isotope.isotope_comms_lib as icl
from typing import Generic, TypeVar
import logging


__pdoc__ = {}
__pdoc__['IsotopePortContainer.__getitem__'] = True
__pdoc__['IsotopePortContainer.__len__'] = True


class PortException(Exception):
    """General exception class for the PortController class.
    """
    pass


class IsotopePort:
    """
    The IsotopePort class is the abstract for all output and input ports on the Isotope Board.
    """

    def __init__(self, comms: icl.Isotope_comms_protocol, port_id: int) -> None:
        """
        Args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class 
                that is used to communicate with the Isotope board.
            port_id (int): ID of the port on the Isotope board.
        """
        self._logger = logging.getLogger(__package__)
        self._comms = comms
        self._id = port_id

    @property
    def id(self) -> int:
        """Get the ID of the port.

        Returns:
            int: The ID of the port.
        """
        return self._id


T = TypeVar('T', bound=IsotopePort)


class IsotopePortContainer(Generic[T]):
    """The IsotopePortContainer class is an abstract for list-like container for IsotopePort objects representing all the corresponding ports on the Isotope board.
    """

    def __init__(self, comms: icl.Isotope_comms_protocol, max_port_count: int) -> None:
        """
        Args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class 
                that is used to communicate with the Isotope board.
            max_port_count (int): The maximum number of ports for the specific port type on the Isotope board.
        """
        self._comms = comms
        self._max_port_count = max_port_count
        self._ports: list[T] = []

    def __getitem__(self, key: int) -> T:
        """Get the specific IsotopePort object by index.

        Implements the `[]` operator to get the IsotopePort object by index, e.g. `port[0]`.

        Args:
            key (int): The index of the motor port.

        Returns:
            T: The IsotopePort object.
        """
        if key < 0 or key > self._max_port_count - 1:
            raise IndexError(f"Invalid port ID. Valid values are {', '.join([str(i) for i in range(0, self._max_port_count)])}.")
        return self._ports[key]

    def __len__(self) -> int:
        """Get the number of ports.

        Implements the `len()` function to return the number of ports in the container.

        Returns:
            int: The number of ports.
        """
        return len(self._ports)
    