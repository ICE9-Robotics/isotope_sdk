"""Contains `MotorPort` and `Motor` classes, used to handle the communication with the MOT ports on the Isotope board.

`MotorPort` class inherits from the `isotope.port.isotope_port.IsotopePort` class as the actual implementation of the communicaiton protocol 
while the `Motor` class inherits from the `isotope.port.isotope_port.IsotopePortContainer` class as a list-like container that holds `MotorPort` 
instances for all available MOT ports on the Isotope board.

Notes
-----
Users are encouraged to use the isotope.Isotope class to access the ports instead of creating their own instances of these 
class directly.

Example
-------

    import isotope

    resolution = 7.5
    current = 400
    rpm = 50
    
    usb_address = 'COM3'
    port_id = 0

    # Start the communication
    isot = isotope.Isotope(usb_address)
    isot.connect()

    # Get motor port at port_id
    motor = isot.motors[port_id]
    
    # Configure motor port
    motor.configure(resolution, current, rpm)

    # Enable the motor port
    result = motor.enable()

    if not result or not motor.is_enabled():
        raise Exception("Failed to enable motor port.")

    # Rotate the motor by 100 steps
    motor.rotate_by_steps(100)

    # Rotate the motor by 90 degrees
    motor.rotate_by_degrees(90)

    # Disable the motor port
    motor.disable()

    # Close the connection
    isot.disconnect()


See Also
--------
isotope.isotope
"""

import isotope.isotope_comms_lib as icl
from .isotope_port import IsotopePort, IsotopePortContainer


class MotorPort(IsotopePort):
    """The MotorPort class is used to control the MOT ports, i.e. MOT 0, 1, 2 and 3, on the Isotope board.
    """

    def __init__(self, comms: icl.Isotope_comms_protocol, port_id: int) -> None:
        """
        Args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class 
                that is used to communicate with the Isotope board.
            port_id (int): ID of the MOT port on the Isotope board. Valid values are 0, 1, 2 and 3.

        Raises:
            ValueError: Invalid port ID. Valid values are 0, 1, 2 and 3.
        """
        if port_id < 0 or port_id > 3:
            raise ValueError("Invalid port ID. Valid values are 0, 1, 2 and 3.")
        super().__init__(comms, port_id)
           
        self._resolution = 0
        self._rpm = 0
        self._current = 0
        self._enabled = False
        self._configure_requested = False
        self._configured = False

    def configure(self, resolution: int, current: int, rpm: int = 100) -> bool:
        """Setup the motor with the specified parameters.

        Args:
            resolution (int): Step resolution of the motor in degrees. Refer to the motor's data sheet for this value.
            current (int): Desired current value in milli amperes. Refer to the motor's data sheet for this value.
                    Note that higher current values will allow the motor to deliver more torque, but will also cause 
                    the motor to heat up more quickly. 
            rpm (int, optional): Desired speed value in RPM. Defaults to 100.
                    Note that the motor may skip steps if the RPM is set too high.

        Returns:
            bool: True if the motor was successfully configured, False otherwise.

        Raises:
            ValueError: Resolution must be positive values.
            ValueError: RPM must be positive values.
            ValueError: Current must be positive values.
        """
        if resolution < 0:
            raise ValueError("Resolution must be a positive value.")
        if rpm < 0:
            raise ValueError("RPM must be a positive value.")
        if current < 0:
            raise ValueError("Current must be a positive value.")

        self._configured = False
        self._configure_requested = True
        self._resolution = resolution
        self._rpm = rpm
        self._current = current

        try:
            self._configure()
        except icl.IsotopeCommsError:
            pass

    @property
    def rpm(self) -> int:
        """Get the configured RPM value of the motor.

        Returns:
            int: The current RPM value of the motor.
        """
        return self._rpm

    @property
    def current(self) -> int:
        """Get the configured current value of the motor in milli amperes.

        Returns:
            int: The current value of the motor in milli amperes.
        """
        return self._current

    @property
    def resolution(self) -> int:
        """Get the configured step resolution of the motor in degrees.

        Returns:
            int: The step resolution of the motor in degrees.
        """
        return self._resolution

    def enable(self) -> bool:
        """Enable the MOT ports. When this function is called, the MOT ports will be switched on and you 
            may notice the connected motor start to heat up.

        Warning: 
            Do not leave the MOT port switched on for extended periods of time at a high current setting 
            as this may cause the motor to overheat.

        Returns:
            bool: True if the MOT port was successfully enabled, False otherwise.
        """
        self._logger.debug(f"Enabling motor {self._id}...")
        if not self._configured:
            self._configure()
        msg = self._comms.send_cmd(
            icl.CMD_TYPE_SET, icl.SEC_MOTOR_ENABLE, self._id, 1)
        if self._comms.is_resp_ok(msg):
            self._enabled = True
            return True
        return False

    def disable(self) -> bool:
        """Disable the MOT ports. When this function is called, the MOT ports will be switched off.

        Returns:
            bool: True if the MOT port was successfully disabled, False otherwise.
        """
        self._logger.debug(f"Disabling motor {self._id}...")
        msg = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_MOTOR_ENABLE, self._id, 0)
        if self._comms.is_resp_ok(msg):
            self._enabled = False
            return True
        return False

    def is_enabled(self) -> bool:
        """Check if the MOT port is enabled.

        Returns:
            bool: True if the MOT port is enabled, False otherwise.
        """
        # Potential vulnerability: The state is not read from the Isotope board, but stored in the class instance.
        return self._enabled

    def rotate_by_steps(self, steps: int) -> bool:
        """Command the motor to rotate by the specified number of steps.
        Note that this function blocks until the motor has completed the specified number of steps. 
        A low RPM value may cause the motor to rotate slowly and cause this function to block for an undesirably long time.

        Args:
            steps (int): The number of steps to rotate the motor by.

        Returns:
            bool: True if the command was successful, False otherwise.
        """
        self._logger.debug(f"Rotating motor {self._id} by {steps} steps...")
        if not self.is_enabled():
            return False
        msg = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_MOTOR_STEP, self._id, steps)
        return self._comms.is_resp_ok(msg)

    def rotate_by_degrees(self, degrees: int) -> bool:
        """Command the motor to rotate by the specified angle in degrees.
        Note that this function blocks until the motor has completed the specified number of steps. 
        A low RPM value may cause the motor to rotate slowly and cause this function to block for an undesirably long time.

        Args:
            degrees (int): The angle in degrees.

        Returns:
            bool: True if the command was successful, False otherwise.
        """
        self._logger.debug(f"Rotating motor {self._id} by {degrees} degrees...")
        steps = degrees/self._resolution
        return self.rotate_by_steps(steps)

    def set_rpm(self, value: int) -> bool:
        """Set the RPM value of the motor.

        Args:
            value (int): The desired RPM value of the motor.

        Returns:
            bool: True if the RPM value was successfully set, False otherwise.
        """
        self._logger.debug(f"Setting RPM to {value}...")
        msg = self._comms.send_cmd(
            icl.CMD_TYPE_SET, icl.SEC_MOTOR_RPM_SPEED, self._id, value)
        if self._comms.is_resp_ok(msg):
            self._rpm = value
            return True
        return False

    def set_current(self, value: int) -> bool:
        """Set the current value of the motor in milli amperes.

        Args:
            value (int): The desired current value of the motor in milli amperes.

        Returns:
            bool: True if the current value was successfully set, False otherwise.
        """
        self._logger.debug(f"Setting current to {value} mA...")
        msg = self._comms.send_cmd(
            icl.CMD_TYPE_SET, icl.SEC_MOTOR_CURRENT_MILLIAMP, self._id, value)
        if self._comms.is_resp_ok(msg):
            self._current = value
            return True
        return False

    def _configure(self) -> bool:
        """Configure the motor with the specified parameters.

        Returns:
            bool: True if the configuration was successful, False otherwise.
        
        Raises:
            IsotopeCommsError: The MotorPort.configure method must be called before calling this method to set the correct parameters.
        """
        if not self._configure_requested:
            raise icl.IsotopeCommsError("Parameters are not set. Have you called the MotorPort.configure method?")
        self._logger.debug(f"Configuring motor {self._id}...")
        result = self.set_rpm(self._rpm) and self.set_current(self._current)
        if result:
            self._configured = True
            self._configure_requested = False
        self._logger.debug(f"{'Successfully configured' if result else 'Failed to configure'} motor {self._id}.")
        return result


class Motor(IsotopePortContainer[MotorPort]):
    """The Motor class is a list-like container for MotorPort objects representing all the MOT ports on the Isotope board.
    """

    def __init__(self, comms: icl.Isotope_comms_protocol) -> None:
        """
        Args:
            comms (isotope_comms_lib.Isotope_comms_protocol): The instance of the Isotope_comms_protocol class 
                that is used to communicate with the Isotope board.
        """
        super().__init__(comms, 4)
        self._ports = [MotorPort(comms, i) for i in range(self._max_port_count)]
