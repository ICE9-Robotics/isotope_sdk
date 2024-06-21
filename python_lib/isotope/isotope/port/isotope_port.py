import logging
from typing import Generic, TypeVar
import isotope.isotope_comms_lib as icl

class PortException(Exception):
    """General exception class for the PortController class.
    """    
    pass

class IsotopePort:
    """
    The IsotopePort class is the abstract for all output and input ports on the Isotope Board.
    """
            
    _id: int = -1
    
    def __init__(self, comms: icl.Isotope_comms_protocol, port_id: int) -> None:
        """Constructor for the IsotopePort class. 

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
    _max_ports: int
    _ports: list[T]
    
    def __init__(self, comms: icl.Isotope_comms_protocol, max_ports: int) -> None:
        """Constructor for the IsotopePortContainer class.

        Args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class 
                that is used to communicate with the Isotope board.
            max_ports (int): The maximum number of ports for the specific port type on the Isotope board.
        """
        self._comms = comms
        self._max_ports = max_ports

    def __getitem__(self, key: int) -> T:
        """Get the specific IsotopePort object by index.

        Args:
            key (int): The index of the motor port.

        Returns:
            T: The IsotopePort object.
        """
        if key < 0 or key > self._max_ports - 1:
            raise ValueError(f"Invalid port ID. Valid values are {', '.join([str(i) for i in range(0, self._max_ports)])}.")
        return self._ports[key]

    def __len__(self) -> int:
        """Get the number of ports.

        Returns:
            int: The number of ports.
        """
        return len(self._ports)
