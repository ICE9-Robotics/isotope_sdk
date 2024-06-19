from typing import Union
import logging
import isotope

class PumpObj:
    """
    The pump object class provides methods for controlling the pumps on the Isotope board.
    
    Attributes:
        rpm (int): The RPM of the motor.
        current (int): The current of the motor.
        steps_per_degree (int): The number of steps per degree of rotation.
        steps_per_ml (int): The number of steps per milliliter.
        default_dir (int): The default direction of the motor.
        _initialised (bool): True if the pump is initialised, False otherwise.
    """
    
    motor: isotope.port.MotorPort
    rpm: int
    current: int
    steps_per_degree: int
    steps_per_ml: int
    default_dir: int
    _initialised: bool = False
    
    def __init__(self) -> None:
        self._logger = logging.getLogger(__package__)
    
    def initialise(self, isotope_board: isotope.Isotope, port_id: int) -> None:
        """
        Initializes the pump object with the specified board and port ID.

        Args:
            isotope_board (isotope.Isotope): The Isotope object.
            port_id (int): The ID of the port to which the motor is connected.
        """
        self._logger.debug(f"Initialising Pump connected to Isotope Breakout {isotope_board} on port {port_id}...")
        
        self.motor = isotope_board.motors[port_id]
        self.motor.configure(self.steps_per_degree, self.current, self.rpm)
        self._initialised = True
    
    def move_liquid_by_steps(self, steps: int) -> bool:
        """
        Moves liquid by rotating the motor with the specified number of steps.

        Args:
            steps (int): The number of steps to rotate the motor. Can be negative to reverse the direction.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        self._logger.debug(f"Moving liquid by {steps} steps...")
        assert(self._initialised, "Pump not initialised.")
        if not self._is_powered():
            self.motor.enable()
        result = self.motor.rotate_by_steps(steps * self.default_dir)
        self.motor.disable()
        self._logger.debug(f"Movement {'successful' if result else 'failed'}.")
        return result
    
    def move_liquid(self, millilitre: float, direction: int) -> bool:
        """
        Moves the specified amount of liquid in milliliters.

        Args:
            millilitre (float): The amount of liquid to move in milliliters.
            direction (int): The direction of movement (-1 for reverse, 1 for forward).
            
        Returns:
            bool: True if the execution is successful, False otherwise.

        Raises:
            ValueError: If millilitre is less than or equal to 0.
            ValueError: If direction is not -1 or 1.
        """
        self._logger.debug(f"Moving liquid by {millilitre} ml...")    
        if millilitre <= 0:
            raise ValueError("millilitre must be greater than 0")
        
        if direction not in [-1, 1]:
            raise ValueError("direction must be either -1 or 1")

        steps = round(self.steps_per_ml * millilitre * direction)
        return self.move_liquid_by_steps(steps)
    
    def _is_powered(self) -> bool:
        """
        Checks if the motor is powered.

        Returns:
            bool: True if the motor is powered, False otherwise.
        """
        return self.motor.is_enabled()

class Pump:
    """
    The Pump class initialises and manages the pump object which provides methods for controlling the pumps on the Isotope board.
    
    Attributes:
        _config (dict[str, any]): configurations for pumps, as specified in config.yaml.
        _isots (isotope.Isotope_comms_protocol,...): Isotope_comms_protocol instances of the installed Isotope boards.
        _pumps (dict[[int | str], PumpObj]): PumpObj instances with the names as the keys.
    """
    
    _config: dict[str, any]
    _isots: tuple[isotope.Isotope,...]
    _pumps: dict[Union[int, str], PumpObj]
    
    def __init__(self, isotope_boards: tuple[isotope.Isotope,...], config: dict):
        """
        Constructor for the Pump class.
        
        Args:
            isotope_boards (tuple[isotope.Isotope,...]): Isotope instances of the installed Isotope boards.
            config (dict): A dictionary containing the configuration settings for the pumps.
        """
        self._logger = logging.getLogger(__package__)
        self._logger.debug("Initialising Pump...")
        self._isots = isotope_boards
        self._config = config['pump']
        self._configure()
        self._logger.debug("Pump initialised.")
    
    def get_names(self) -> list[Union[int, str]]:
        """
        Gets the names of all the pumps.
        
        Returns:
            list[[int | str]]: A list of pump names.
        """
        return list(self._pumps.keys())
    
    def __getitem__(self, name: Union[int, str]) -> PumpObj:
        """
        Gets the pump object with the specified name.
        
        Args:
            name ([int | str]): The name of the pump.
        
        Returns:
            PumpObj: The pump object.
        """
        self._verify_name(name)
        return self._pumps[name]
    
    def _verify_name(self, name: Union[int, str]) -> None:
            """
            Verifies if a pump with the given name exists.

            Args:
                name ([int | str]): The name of the pump to verify.

            Raises:
                ValueError: If the pump with the given name is not found.
            """
            if name not in self._pumps:
                raise ValueError(f"Pump with name {name} not found.")
        
    def _configure(self):
        """
        Configures pumps based on the provided configuration settings.
        """
        self._logger.debug(f"Configuring pumps... Registered ${len(self._config['devices'])}.")
        
        defaults = self._config['defaults']
        self._pumps = {}
        for device in self._config['devices']:
            self._logger.debug(f"Configuring Pump ${device['name']}...")
            pump = PumpObj()
            pump.rpm = device.get('rpm', defaults['rpm'])
            pump.current = device.get('current', defaults['current'])
            pump.steps_per_degree = device.get('steps_per_degree', defaults['steps_per_degree'])
            pump.steps_per_ml = device.get('steps_per_ml', defaults['steps_per_ml'])
            pump.default_dir = -1 if device.get('reverse_direction', defaults['reverse_direction']) else 1
            pump.initialise(self._isots[device['board_id']], device['port_id'])
            self._pumps[device['name']] = pump
            self._logger.debug(f"Pump ${device['name']} configured.")
