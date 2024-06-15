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
        _valves (dict[int, ValveObj]): ValveObj instances.
    """
    
    _config: dict[str, any]
    _isots: tuple[isotope.Isotope,...]
    _valves: dict[int, ValveObj]
    
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
        
    def get_device_ids(self) -> list[int]:
        """
        Gets the IDs of all the valves.
        
        Returns:
            list[int]: A list of valve IDs.
        """
        return list(self._valves.keys())
        
    def open(self, device_id: int) -> bool:
        """
        Opens the specified valve.

        Args:
            device_id (int): The ID of the valve device.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        self._verify_device_id(device_id)
        return self._valves[device_id].open()
    
    def close(self, device_id: int) -> bool:
        """
        Close the specified valve.

        Args:
            device_id (int): The ID of the valve device.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        self._verify_device_id(device_id)
        return self._valves[device_id].close()
    
    def toggle(self, device_id: int) -> bool:
        """
        Toggles the specified valve.

        Args:
            device_id (int): The ID of the valve device.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        self._verify_device_id(device_id)
        if self.is_open(device_id):
            return self.close(device_id)
        else:
            return self.open(device_id)
    
    def is_open(self, device_id: int) -> bool:
        """
        Checks if the specified valve is open.

        Args:
            device_id (int): The ID of the valve device.

        Returns:
            bool: True if the valve is open, False otherwise.
        """
        self._verify_device_id(device_id)
        return self._valves[device_id].is_open()
    
    def _verify_device_id(self, device_id: int) -> None:
            """
            Verifies if a valve with the given ID exists.

            Args:
                device_id (int): The ID of the valve to verify.

            Raises:
                ValueError: If the valve with the given ID is not found.
            """
            if device_id not in self._valves:
                raise ValueError(f"Valve with ID {device_id} not found.")
        
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
            self._valves[device['id']] = valve
