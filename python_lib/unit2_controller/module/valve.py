from typing import Union
import isotope

class ValveObj:
    """
    The valve object class.
    """
    
    power_output: isotope.port.PowerOutputPort
    normally_open: bool
    
    def initialise(self, isot: isotope.Isotope, port_id: int) -> None:
        """
        Initializes the valve object with the specified board and port ID.

        Args:
            isot (isotope.Isotope): The Isotope instance for controlling the board.
            port_id (int): The ID of the power output port to which the valve is connected.
        """
        self.power_output = isot.powers[port_id]
        self.power_output.default_pwm = 1024
    
    def open(self) -> bool:
        """
        Open the valve.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        return self.power_output.disable() if self.normally_open else self.power_output.enable()
    
    def close(self) -> bool:
        """
        Close the valve.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
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
    Class for controlling Unit 2 diaphragm valves.
    
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
        self._isots = isotope_boards
        self._config = config['valve']
        self._configure()
        
    def get_names(self) -> list[Union[int, str]]:
        """
        Gets the names of all the valves.
        
        Returns:
            list[[int | str]]: A list of the names of the valves.
        """
        return list(self._valves.keys())
        
    def open(self, name: Union[int, str]) -> bool:
        """
        Opens the specified valve.

        Args:
            name ([int | str]): The name of the valve device.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        self._verify_name(name)
        return self._valves[name].open()
    
    def close(self, name: Union[int, str]) -> bool:
        """
        Close the specified valve.

        Args:
            name ([int | str]): The name of the valve device.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        self._verify_name(name)
        return self._valves[name].close()
    
    def toggle(self, name: Union[int, str]) -> bool:
        """
        Toggles the specified valve.

        Args:
            name ([int | str]): The name of the valve device.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        self._verify_name(name)
        if self.is_open(name):
            return self.close(name)
        else:
            return self.open(name)
    
    def is_open(self, name: Union[int, str]) -> bool:
        """
        Checks if the specified valve is open.

        Args:
            name ([int | str]): The name of the valve device.

        Returns:
            bool: True if the valve is open, False otherwise.
        """
        self._verify_name(name)
        return self._valves[name].is_open()
    
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
        defaults = self._config['defaults']
        self._valves = {}
        for device in self._config['devices']:
            valve = ValveObj()
            valve.normally_open = device.get('normally_open', defaults['normally_open'])
            valve.initialise(self._isots[device['board_id']], device['port_id'])
            self._valves[device['name']] = valve
