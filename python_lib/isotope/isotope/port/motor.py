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
    motor_1_port_id = 0
    motor_2_port_id = 1

    # Start the communication
    isot = isotope.Isotope(usb_address)
    isot.connect()

    # Get motor instances
    motor1 = isot.motors[motor_1_port_id]
    motor2 = isot.motors[motor_2_port_id]
    
    # Configure motor ports
    motor1.configure(resolution, current, rpm)
    motor2.configure(resolution, current, rpm)

    # Enable the motor ports
    result = motor1.enable() and motor2.enable()    

    if not result or not motor1.is_enabled() or not motor2.is_enabled():
        raise Exception("Failed to enable motor ports.")

    # Rotate the motor by 100 steps
    motor1.rotate_by_steps(100)
    motor2.rotate_by_steps(80)
    motor1.wait_until_motion_completed()
    motor2.wait_until_motion_completed()

    # Rotate the motor by 90 degrees
    motor1.rotate_by_degrees(90)

    # Disable the motor port
    motor1.disable()

    # Close the connection
    isot.disconnect()


See Also
--------
isotope.isotope
"""

import time
import isotope.isotope_comms_lib as icl
from isotope.isotope_exceptions import IsotopeCommsError, InvalidOperationException
from .isotope_port import IsotopePort, IsotopePortContainer


class MotorPort(IsotopePort):
    """The MotorPort class is used to control the MOT ports, i.e. MOT 0, 1, 2 and 3, on the Isotope board.
    """

    def __init__(self, comms: icl.IsotopeCommsProtocol, port_id: int) -> None:
        """
        Args:
            comms (isotope_comms_lib.IsotopeCommsProtocol): The instance of the IsotopeCommsProtocol class 
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
        self._busy = False
        self._current_sequence = 0
        self._last_is_busy_query_time = 0
        self._is_busy_query_delay = 0.1

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
        except IsotopeCommsError:
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
        resp = self._comms.send_cmd(
            icl.CMD_TYPE_SET, icl.SEC_MOTOR_ENABLE, self._id, 1)
        if self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded:
            self._enabled = True
            self._busy = False  # Motion is always stopped when enabling the motor
            return True
        return False

    def disable(self) -> bool:
        """Disable the MOT ports. When this function is called, the MOT ports will be switched off.

        Returns:
            bool: True if the MOT port was successfully disabled, False otherwise.
        """
        self._logger.debug(f"Disabling motor {self._id}...")
        resp = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_MOTOR_ENABLE, self._id, 0)
        if self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded:
            self._enabled = False
            self._busy = False  # Motion is always stopped when disabling the motor
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
            
        Raises:
            InvalidOperationException: Motor is not enabled.
        """
        self._logger.debug(f"Rotating motor {self._id} by {steps} steps...")
        if not self.is_enabled():
            raise InvalidOperationException("Motor is not enabled.")
        resp = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_MOTOR_STEP, self._id, steps)
        self._last_is_busy_query_time = time.perf_counter()
        if self._comms.is_resp_ok(resp) == icl.CmdResponseType.Acknowledged:
            self._busy = True
            self._current_sequence = resp.sequence
            return True
        if self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded:  # SUCCESS is received, motion completed within 1 microsecond??
            return True
        return False

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
        resp = self._comms.send_cmd(
            icl.CMD_TYPE_SET, icl.SEC_MOTOR_RPM_SPEED, self._id, value)
        if self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded:
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
        resp = self._comms.send_cmd(
            icl.CMD_TYPE_SET, icl.SEC_MOTOR_CURRENT_MILLIAMP, self._id, value)
        if self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded:
            self._current = value
            return True
        return False

    def set_resolution(self, value: int) -> bool:
        """Set the step resolution of the motor in degrees.

        Args:
            value (int): The desired step resolution of the motor in degrees.

        Returns:
            bool: True if the step resolution was successfully set, False otherwise.
        """
        self._logger.debug(f"Setting resolution to {value} degrees...")
        resp = self._comms.send_cmd(icl.CMD_TYPE_SET, icl.SEC_MOTOR_STEP_ANGLE, self._id, value)
        if self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded:
            self._resolution = value
            return True
        return False

    def is_motion_completed(self) -> bool:
        """Check if a `CMD_SUCCESS` message has been received which is sent by the Isotope board as soon as the previously requested motion is completed.

        Returns:
            bool: True if the motor has completed the motion, False otherwise.
        """
        if not self._busy:
            return True  # No motion is in progress
        resp = self._comms.retrieve_response(self._current_sequence)
        if self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded or self._comms.is_resp_ok(resp) == icl.CmdResponseType.Aborted:
            return True
        if time.perf_counter() - self._last_is_busy_query_time > self._is_busy_query_delay:
            return not self.is_busy_from_board()
        return False

    def wait_until_motion_completed(self, timeout = 0, check_frequency=100):
        """Wait until a `CMD_SUCCESS` message is received which is sent by the Isotope board as soon as the previously requested motion is completed.

        Args:
            timeout (int, optional): Set a timeout in seconds. Set to zero or a negative value to disable and wait indefinitely. Defaults to 0.
            check_frequency (int, optional): Set a frequency in Hz for repeated checking of the motion status. Defaults to 100 Hz.
        """
        delay = 1/check_frequency
        t_start = time.perf_counter()
        while not self.is_motion_completed() and (timeout <= 0 or time.perf_counter() - t_start < timeout):
            time.sleep(delay)
            
    def is_busy_from_board(self) -> bool:
        """Check if the motor is busy. This method sends a message to the Isotope board to ask for a feedback on the busy status of the motor.
        This method is different from `MotorPort.is_motion_completed()` which checks if a `CMD_SUCCESS` message is received from the board.
        A `CMD_SUCCESS` message is sent from the board as soon as the motor completes its motion. Therefore, `MotorPort.is_motion_completed()` is more
        efficient in that it does not send a message to the board. However, in rare situations, the `CMD_SUCCESS` message may be dropped due to communication errors. 
        This method, in this case, can be used to proactively ask for an update on the busy status of the motor. 
        
        Frequent use of this method is discouraged as it may cause unnecessary communication overhead.

        Returns:
            bool: True if the motor is busy, False otherwise.
        """
        resp = self._comms.send_cmd(icl.CMD_TYPE_GET, icl.SEC_MOTOR_BUSY, self._id)
        self._last_is_busy_query_time = time.perf_counter()
        if self._comms.is_resp_ok(resp) == icl.CmdResponseType.Succeeded:
            return resp.payload == 1

    def _configure(self) -> bool:
        """Configure the motor with the specified parameters.

        Returns:
            bool: True if the configuration was successful, False otherwise.

        Raises:
            InvalidOperationException: If parameters are not set. The `MotorPort.configure()` method must be called before calling this method to set the correct parameters.
        """
        if not self._configure_requested:
            raise InvalidOperationException("Parameters are not set. Have you called the MotorPort.configure method to set motor parameters?")
        self._logger.debug(f"Configuring motor {self._id}...")
        result = self.set_rpm(self._rpm) and self.set_current(self._current) and self.set_resolution(self._resolution)
        if result:
            self._configured = True
            self._configure_requested = False
        self._logger.debug(f"{'Successfully configured' if result else 'Failed to configure'} motor {self._id}.")
        return result


class Motor(IsotopePortContainer[MotorPort]):
    """The Motor class is a list-like container for MotorPort objects representing all the MOT ports on the Isotope board.
    """

    def __init__(self, comms: icl.IsotopeCommsProtocol) -> None:
        """
        Args:
            comms (isotope_comms_lib.IsotopeCommsProtocol): The instance of the IsotopeCommsProtocol class 
                that is used to communicate with the Isotope board.
        """
        super().__init__(comms, 4)
        self._ports = [MotorPort(comms, i) for i in range(self._max_port_count)]
