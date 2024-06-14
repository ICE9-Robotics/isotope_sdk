import isotope.isotope_comms_lib as icl

class PortException(Exception):
    """General exception class for the PortController class.
    """    
    pass

class IsotopePort:
    _id: int = -1
    _enabled: bool = False

    def __init__(self, isotope: icl.Isotope_comms_protocol, port_id: int) -> None:
        """Constructor for the PortController class. This class is an abstract for all output and input communication/power ports on the Isotope Board.

        Args:
            isotope (icl.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class that is used to communicate with the Isotope board.
            port_id (int): ID of the port on the Isotope board.
        """        

        self._isotope = isotope
        self._id = id
            
    def __del__(self):
        """Destructor for the PortController class.
        """
        try:
            self.disable()
        except:
            pass

    def enable(self) -> bool:
        """Abstract method to enable the port. This method must be implemented in the derived class.
        """        
        raise NotImplementedError("This method must be implemented in the derived class.")

    def disable(self) -> bool:
        """Abstract method to disable the port. This method must be implemented in the derived class.
        """
        raise NotImplementedError("This method must be implemented in the derived class.")

    def is_enabled(self) -> bool:
        """Check if the port is enabled.

        Returns:
            bool: True if the port is enabled, False otherwise.
        """        
        return self._enabled