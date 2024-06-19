import logging
from typing import Union
import isotope

class ValveObj:
    """
    The valve object class provides methods for controlling the valves on the Isotope board.
    
    Attributes:s
        normally_open (bool): The state of the valve when it is not powered.
    """
    
    power_output: isotope.port.PowerOutputPort
    normally_open: bool
    
    def __init__(self) -> None:
        self._logger = logging.getLogger(__package__)
    
    def initialise(self, isot: isotope.Isotope, port_id: int) -> None:
        """
        Initializes the valve object with the specified board and port ID.

        Args:
            isot (isotope.Isotope): The Isotope instance for controlling the board.
            port_id (int): The ID of the power output port to which the valve is connected.
        """
        self._logger.debug(f"Initialising Valve connected to Isotope Breakout {isot} on port {port_id}...")
        self.power_output = isot.powers[port_id]
        self.power_output.default_pwm = 1024
    
    def open(self) -> bool:
        """
        Open the valve.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        self._logger.debug("Opening valve...")
        return self.power_output.disable() if self.normally_open else self.power_output.enable()
    
    def close(self) -> bool:
        """
        Close the valve.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        self._logger.debug("Closing valve...")
        return self.power_output.enable() if self.normally_open else self.power_output.disable()
    
    def toggle(self) -> bool:
        """
        Toggles the valve.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        return self.close() if self.is_open() else self.open()
    
    def is_open(self) -> bool:
        """
        Checks if the valve is open.

        Returns:
            bool: True if the valve is on, False otherwise.
        """
        return self.power_output.is_enabled()

class Valve:
    """
    The Valve class initialises and manages the valve objects which provides methods for controlling the valves on the Isotope board.
    
    Attributes:
        _config (dict[str, any]): configuration for valves, as specified in config.yaml.
        _isots (isotope.Isotope_comms_protocol,...): Isotope_comms_protocol instances of the installed Isotope boards.
        _valves (dict[[int | str], ValveObj]): ValveObj instances with device names as the keys.
    """
    
    _config: dict[str, any]
    _isots: tuple[isotope.Isotope,...]
    _valves: dict[Union[int, str], ValveObj]
    
    def __init__(self, isotope_boards: tuple[isotope.Isotope,...], config: dict):
        """
        Constructor for the Valve class.
        
        Args:
            isotope_boards (tuple[isotope.Isotope,...]): Isotope instances of the installed Isotope boards.
            config (dict): A dictionary containing the configuration settings for the valves.
        """
        self._logger = logging.getLogger(__package__)
        self._logger.debug("Initialising Valve...")
        self._isots = isotope_boards
        self._config = config['valve']
        self._configure()
        self._logger.debug("Valve initialised.")
        
    def get_names(self) -> list[Union[int, str]]:
        """
        Gets the names of all the valves.
        
        Returns:
            list[[int | str]]: A list of the names of the valves.
        """
        return list(self._valves.keys())
        
    def __getitem__(self, name: Union[int, str]) -> ValveObj:
        """
        Gets the valve object with the specified name.

        Args:
            name ([int | str]): The name of the valve.

        Returns:
            ValveObj: The valve object.
        """
        self._verify_name(name)
        return self._valves[name]
    
    def _verify_name(self, name: Union[int, str]) -> None:
            """
            Verifies if a valve with the given name exists.

            Args:
                name ([int | str]): The name of the valve to verify.

            Raises:
                ValueError: If the valve with the given name is not found.
            """
            if name not in self._valves:
                raise ValueError(f"Valve with name {name} not found.")
        
    def _configure(self):
        """
        Configures valves based on the provided configuration settings.
        """
        self._logger.debug(f"Configuring valves... Registered ${len(self._config['devices'])}.")
        defaults = self._config['defaults']
        self._valves = {}
        for device in self._config['devices']:
            self._logger.debug(f"Configuring Valve ${device['name']}...")
            valve = ValveObj()
            valve.normally_open = device.get('normally_open', defaults['normally_open'])
            valve.initialise(self._isots[device['board_id']], device['port_id'])
            self._valves[device['name']] = valve
            self._logger.debug(f"Valve ${device['name']} configured.")
