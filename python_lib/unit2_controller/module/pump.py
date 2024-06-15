import isotope

class PumpObj:
    """
    The pump object class.
    """
    
    motor: isotope.port.MotorPort
    rpm: int
    current: int
    steps_per_degree: int
    steps_per_ml: int
    default_dir: int
    
    def initialise(self, isotope_board: isotope.Isotope, port_id: int) -> None:
        """
        Initializes the pump object with the specified board and port ID.

        Args:
            isotope_board (isotope.Isotope): The Isotope object.
            port_id (int): The ID of the port to which the motor is connected.
        """
        self.motor = isotope_board.motors[port_id]
        self.motor.configure(self.steps_per_degree, self.current, self.rpm)        
    
    def rotate_by_steps(self, steps: int) -> bool:
        """
        Rotates the motor by the specified number of steps.

        Args:
            steps (int): The number of steps to rotate the motor. Can be negative to reverse the direction.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        if not self.is_powered():
            self.motor.enable()
        result = self.motor.rotate_by_steps(steps * self.default_dir)
        self.motor.disable()
        return result
    
    def move_liquid_by_ml(self, millilitre: float, direction: int) -> bool:
        """
        Moves the specified amount of liquid in milliliters.

        Args:
            millilitre (float): The amount of liquid to move in milliliters.
            direction (int): The direction of movement (-1 for reverse, 1 for forward).

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        assert(millilitre > 0)
        assert(direction in [-1, 1])
        
        steps = round(self.steps_per_ml * millilitre * direction)
        return self.rotate_by_steps(steps)
    
    def is_powered(self) -> bool:
        """
        Checks if the motor is powered.

        Returns:
            bool: True if the motor is powered, False otherwise.
        """
        return self.motor.is_enabled()

class Pump:
    """
    Class for controlling Unit 2 diaphragm pumps.
    
    Attributes:
        _config (dict[str, any]): configurations for pumps, as specified in config.yaml.
        _isots (isotope.Isotope_comms_protocol,...): Isotope_comms_protocol instances of the installed Isotope boards.
        _pumps (dict[int, PumpObj]): PumpObj instances.
    """
    
    _config: dict[str, any]
    _isots: tuple[isotope.Isotope,...]
    _pumps: dict[int, PumpObj]
    
    def __init__(self, isotope_boards: tuple[isotope.Isotope,...], config: dict):
        """
        Constructor for the Pump class.
        
        Args:
            isotope_boards (tuple[isotope.Isotope,...]): Isotope instances of the installed Isotope boards.
            config (dict): A dictionary containing the configuration settings for the pumps.
        """
        self._isots = isotope_boards
        self._config = config['pump']
        self._configure()
    
    def get_device_ids(self) -> list[int]:
        """
        Gets the IDs of all the pumps.
        
        Returns:
            list[int]: A list of pump IDs.
        """
        return list(self._pumps.keys())
        
    def move_liquid(self, device_id: int, millilitre: float, direction: int = 1) -> bool:
        """
        Moves the liquid in the specified pump by the given volume.
        
        Args:
            device_id (int): The ID of the pump.
            millilitre (float): The volume of liquid to be moved in milliliters.
            direction (int, optional): The direction of movement, can be either -1 or 1. Defaults to 1.
        
        Returns:
            bool: True if the execution is successful, False otherwise.
        
        Raises:
            ValueError: If millilitre is less than or equal to 0.
            ValueError: If direction is not -1 or 1.
        """
        self._verify_device_id(device_id)
        
        if millilitre <= 0:
            raise ValueError("millilitre must be greater than 0")
        
        if direction not in [-1, 1]:
            raise ValueError("direction must be either -1 or 1")
        
        return self._pumps[device_id].move_liquid_by_ml(millilitre, direction)
    
    def move_liquid_by_steps(self, device_id: int, steps: int) -> bool:
        """
        Moves the liquid in the specified pump motor by the given number of steps.
        
        Args:
            device_id (int): The ID of the pump.
            steps (int): The number of steps. Can be negative to reverse the direction.
        
        Returns:
            bool: True if the movement is successful, False otherwise.
        """
        self._verify_device_id(device_id)
        return self._pumps[device_id].rotate_by_steps(steps)
    
    def _verify_device_id(self, device_id: int) -> None:
            """
            Verifies if a pump with the given ID exists.

            Args:
                device_id (int): The ID of the pump to verify.

            Raises:
                ValueError: If the pump with the given ID is not found.
            """
            if device_id not in self._pumps:
                raise ValueError(f"Pump with ID {device_id} not found.")
        
    def _configure(self):
        """
        Configures pumps based on the provided configuration settings.
        """
        defaults = self._config['defaults']
        self._pumps = {}
        for device in self._config['devices']:
            pump = PumpObj()
            pump.rpm = device.get('rpm', defaults['rpm'])
            pump.current = device.get('current', defaults['current'])
            pump.steps_per_degree = device.get('steps_per_degree', defaults['steps_per_degree'])
            pump.steps_per_ml = device.get('steps_per_ml', defaults['steps_per_ml'])
            pump.default_dir = -1 if device.get('reverse_direction', defaults['reverse_direction']) else 1
            self._pumps[device['id']] = pump
