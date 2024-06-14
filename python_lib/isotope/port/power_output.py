import isotope.isotope_comms_lib as icl
from .isotope_port import IsotopePort, PortException


class PowerOutput(IsotopePort):

    _defaut_pwm: int
    _current_pwm: int

    def __init__(self, isotope: icl.Isotope_comms_protocol, port_id: int, pwm_val: int = 1024) -> None:
        """Constructor for the PowerOutput class. This class is used to control the power output ports, i.e. Output 0, 1 and 2, on the Isotope board.

        Args:
            isotope (icl.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class that is used to communicate with the Isotope board.
            port_id (int): ID of the power output port on the Isotope board. Valid values are 0, 1 and 2.
            pwm_val (int): PWM value to set the power output to. Valid values are 0 to 1024. Defaults to 1024.

        Raises:
            ValueError: Invalid port ID. Valid values are 0, 1 and 2.
            ValueError: PWM value must be between 0 and 1024.
        """        

        if port_id < 0 or port_id > 2:
            raise ValueError("Invalid port ID. Valid values are 0, 1 and 2.")
        
        if pwm_val < 0 or pwm_val > 1024:
            raise ValueError("PWM value must be between 0 and 1024.")
        
        super().__init__(isotope, port_id)
        self._defaut_pwm = pwm_val
        
    def enable(self, pwm: int=None) -> bool:
        """Enable the power output ports. When this function is called, voltage will be applied cross the terminals of the power output port. The current limit is configured by the PWM value. 
        
        pwm (int, optional): Sets the current limit of the power output port. Valid values are 0 to 1024. Defaults to the value set in the constructor.
            Note that a value of 0 is equivalent to disabling the power output port by calling the disable() function.
        
        Returns:
            bool: True if the power output port was successfully enabled, False otherwise.
            
        Raises:
            ValueError: PWM value must be between 0 and 1024.
        """
        if pwm is not None and (pwm < 0 or pwm > 1024):
            raise ValueError("PWM value must be between 0 and 1024.")
        if pwm == 0:
            return self.disable()
        if pwm is None:
            pwm = self._defaut_pwm
        success = self._isotope.set_power_output(self._id, pwm)
        if success:
            self._enabled = True
            self._current_pwm = pwm
        return success

    def disable(self) -> bool:
        """Disable the power output ports. When this function is called, the power output ports will be switched off.

        Returns:
            bool: True if the power output port was successfully disabled, False otherwise.
        """        
        success = self._isotope.set_power_output(self._id, 0)
        if success:
            self._enabled = False
            self._current_pwm = 0
        return success
    
    def get_pwm(self) -> int:
        """Get the current PWM value of the power output port.

        Returns:
            int: The current PWM value of the power output port.
        """        
        return self._current_pwm
    
    def get_default_pwm(self) -> int:
        """Get the default PWM value of the power output port as set in the constructor.

        Returns:
            int: The default PWM value of the power output port.
        """        
        return self._defaut_pwm
    