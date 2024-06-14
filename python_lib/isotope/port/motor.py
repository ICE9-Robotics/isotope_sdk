import isotope.isotope_comms_lib as icl
from .isotope_port import IsotopePort, PortException


class Motor(IsotopePort):

    _resolution: int
    _rpm: int
    _current: int

    def __init__(self, isotope: icl.Isotope_comms_protocol, port_id: int, resolution: int, current: int, rpm: int = 100) -> None:
        """Constructor for the Motor class. This class is used to control the MOT ports, i.e. MOT 0, 1, 2 and 3, on the Isotope board.

        Args:
            isotope (icl.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class that is used to communicate with the Isotope board.
            port_id (int): ID of the MOT port on the Isotope board. Valid values are 0, 1, 2 and 3.
            resolution (int): Step resolution of the motor in degrees. Refer to the motor's data sheet for this value.
            current (int): Desired current value in milli amperes. Refer to the motor's data sheet for this value.
                    Note that higher current values will allow the motor to deliver more torque, but will also cause the motor to heat up more quickly. 
            rpm (int, optional): Desired speed value in RPM. Defaults to 100.
                    Note that the motor may skip steps if the RPM is set too high.

        Raises:
            ValueError: Resolution must be positive values.
            ValueError: RPM must be positive values.
            ValueError: Current must be positive values.
            PortException: Could not configure the MOT port with the given parameters.
        """        
        
        if port_id < 0 or port_id > 3:
            raise ValueError("Invalid port ID. Valid values are 0, 1, 2 and 3.")
        if resolution < 0:
            raise ValueError("Resolution must be a positive value.")
        if rpm < 0:
            raise ValueError("RPM must be a positive value.")
        if current < 0:
            raise ValueError("Current must be a positive value.")
        
        super().__init__(isotope, port_id)
        self._resolution = resolution
        self._rpm = rpm
        self._current = current
        
        if not self._configure():
            raise PortException(
                f"Could not configure MOT port {port_id} with the given parameters.")

    def enable(self) -> bool:
        """Enable the MOT ports. When this function is called, the MOT ports will be switched on and you may notice the connected motor start to heat up.
            Warning: Do not leave the MOT port switched on for extended periods of time at a high current setting as this may cause the motor to overheat.
        
        Returns:
            bool: True if the MOT port was successfully enabled, False otherwise.
        """
        success = self._isotope.set_motor_enable(self._id, 1)
        if success:
            self._enabled = True
        return success

    def disable(self) -> bool:
        """Disable the MOT ports. When this function is called, the MOT ports will be switched off.

        Returns:
            bool: True if the MOT port was successfully disabled, False otherwise.
        """        
        success = self._isotope.set_motor_enable(self._id, 0)
        if success:
            self._enabled = False
        return success

    def get_rpm(self) -> int:
        """Get the configured RPM value of the motor.

        Returns:
            int: The current RPM value of the motor.
        """        
        return self._rpm

    def get_current(self) -> int:
        """Get the configured current value of the motor in milli amperes.

        Returns:
            int: The current value of the motor in milli amperes.
        """        
        return self._current
    
    def get_resolution(self) -> int:
        """Get the configured step resolution of the motor in degrees.

        Returns:
            int: The step resolution of the motor in degrees.
        """        
        return self._resolution

    def rotate_by_steps(self, steps: int) -> bool:
        """Command the motor to rotate by the specified number of steps.
        Note that this function blocks until the motor has completed the specified number of steps. A low RPM value may cause the motor to rotate slowly and cause this function to block for an undesirably long time.

        Args:
            steps (int): The number of steps to rotate the motor by.

        Returns:
            bool: True if the command was successful, False otherwise.
        """        
        if not self._enabled:
            return False
        success = self._isotope.set_motor_step(self._id, round(steps))
        return success

    def rotate_by_degrees(self, degrees: int) -> bool:
        """Command the motor to rotate by the specified angle in degrees.
        Note that this function blocks until the motor has completed the specified number of steps. A low RPM value may cause the motor to rotate slowly and cause this function to block for an undesirably long time.

        Args:
            degrees (int): The angle in degrees.

        Returns:
            bool: True if the command was successful, False otherwise.
        """        
        steps = degrees/self._resolution
        return self.rotate_by_steps(steps)

    def _configure(self) -> bool:
        """[Class private] Configure the motor with the specified parameters.

        Returns:
            bool: True if the configuration was successful, False otherwise.
        """
        return self._isotope.set_motor_rpm(self._id, self._rpm) and self._isotope.set_motor_current_milliamps(self._id, self._current)
