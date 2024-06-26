"""Contains `ValveObj` and `Valve` classes, used to control solenoids connected to the Isotope board.

`ValveObj` class inherits from the `unit2_controller.module.device.DeviceObj` class containing the actual implementation of functions to control the valves. 
`Valve` class inherits from the `unit2_controller.module.device.Device` class that initialises and manages the `ValveObj` instances for all registered valves.

Notes
-----
Users are encouraged to use the `unit2_controller.unit2_controller.Unit2` class to access the valves instead of creating their own instances of these 
class directly.

Example
-------
    from unit2_controller import Unit2


    def setup_unit2():
        # Create a Unit2 object, see example_config.yaml for an example configuration file
        unit2 = Unit2('config.yaml')
        unit2.connect()
        return unit2
        
        
    unit2 = setup_unit2()
    # Test the valve
    for name, valve in unit2.valve.items():
        if valve.open() and valve.is_open():
            print(f"opened Valve {name}")
        else:
            raise Exception(f"Failed to open Valve {name}")
        
        if valve.close() and not valve.is_open():
            print(f"closed Valve {name}")
        else:
            raise Exception(f"Failed to close Valve {name}")
        
        opened = valve.open()
        if valve.toggle() and valve.is_open() != opened:
            print(f"toggled Valve {name}")
        else:
            raise Exception(f"Failed to toggle Valve {name}")

        

See Also
--------
unit2_controller.unit2_controller.Unit2
unit2_controller.module.device
"""
import isotope
from .device import Device, DeviceObj


class ValveObj(DeviceObj):
    """The ValveObj class provides methods for controlling the valves on the Isotope board.
    """

    def __init__(self) -> None:
        super().__init__()
        self.normally_open = False
        self.power_output: isotope.port.PowerOutputPort = None

    def initialise(self, isot: isotope.Isotope, port_id: int) -> None:
        """Initializes the valve object with the specified board and port ID.

        Args:
            isot (isotope.Isotope): The Isotope instance for controlling the board.
            port_id (int): The ID of the power output port to which the valve is connected.
        """
        self._logger.debug(f"Initialising Valve connected to Isotope Breakout {isot} on port {port_id}...")
        self.power_output = isot.powers[port_id]
        self.power_output.default_pwm = 1024

    def open(self) -> bool:
        """Open the valve.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        self._logger.debug("Opening valve...")
        return self.power_output.disable() if self.normally_open else self.power_output.enable()

    def close(self) -> bool:
        """Close the valve.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        self._logger.debug("Closing valve...")
        return self.power_output.enable() if self.normally_open else self.power_output.disable()

    def toggle(self) -> bool:
        """ Toggles the valve.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        return self.close() if self.is_open() else self.open()

    def is_open(self) -> bool:
        """Checks if the valve is open.

        Returns:
            bool: True if the valve is on, False otherwise.
        """
        return self.power_output.is_enabled()


class Valve(Device[ValveObj]):
    """ The Valve class initialises and manages the ValveObj instances.
    """

    def __init__(self, isotope_boards: dict[int | str, isotope.Isotope], config: dict):
        """
        Args:
            isotope_boards (dict[int | str, isotope.Isotope]): isotope.Isotope instances of the installed Isotope boards.
            config (dict): A dictionary containing the configuration settings for the valves.
        """
        super().__init__(isotope_boards, config['valve'])

        self._logger.debug("Initialising Valve...")
        self._configure()
        self._logger.debug("Valve initialised.")

    def _configure(self):
        """Configures valves based on the provided configuration settings.
        """
        self._logger.debug(f"Configuring valves... ${len(self._config['devices'])} registered.")
        defaults = self._config['defaults']
        self._devices = {}
        for device in self._config['devices']:
            self._logger.debug(f"Configuring Valve ${device['name']}...")

            board_name = device['board_name']
            if board_name not in self._isots.keys():
                raise ValueError(
                    f"Isotope board {board_name} is not registered. Have you assigned the correct board_name to valve {device['name']} in the config file?")

            port_id = device['port_id']
            if port_id > len(self._isots[board_name].powers):
                raise ValueError(f"Port ID {port_id} is out of range.")
            if port_id < 0:
                raise ValueError(f"Port ID {port_id} is invalid. Port ID must be greater than or equal to 0.")

            valve = ValveObj()
            valve.normally_open = device.get('normally_open', defaults['normally_open'])
            valve.initialise(self._isots[device['board_name']], device['port_id'])
            self._devices[device['name']] = valve
            self._logger.debug(f"Valve ${device['name']} configured.")
