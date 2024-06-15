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
        self._comms = comms
        self._id = port_id
        
    @property
    def id(self) -> int:
        """Get the ID of the port.

        Returns:
            int: The ID of the port.
        """        
        return self._id