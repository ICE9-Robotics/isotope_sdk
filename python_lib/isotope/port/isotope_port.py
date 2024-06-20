import logging
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
    

class IsotopePortContainer:
    """The Motor class is a list-like container for MotorPort objects representing all the MOT ports on the Isotope board.
    """
    _max_ports: int
    _ports: list[IsotopePort]
    
    def __init__(self, comms: icl.Isotope_comms_protocol) -> None:
        """Constructor for the Motor class.

        Args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class 
                that is used to communicate with the Isotope board.
        """
        self._comms = comms

    def __getitem__(self, key: int) -> IsotopePort:
        """Get the motor port by index.

        Args:
            key (int): The index of the motor port.

        Returns:
            MotorPort: The motor port.
        """
        if key < 0 or key > 3:
            raise ValueError("Invalid port ID. Valid values are 0, 1, 2 and 3.")
        return self._ports[key]

    def __len__(self) -> int:
        """Get the number of motor ports.

        Returns:
            int: The number of motor ports.
        """
        return len(self._ports)
