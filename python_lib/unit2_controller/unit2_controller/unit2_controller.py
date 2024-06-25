"""Unit2 Module is for controlling the Nuclear Medicine Unit 2 modular system.

It provides a straightforward interface for controlling the pumps and valves connected to multiple Isotope boards.
Details of the pumps, valves, and Isotope boards can be specified in a configuration file in YAML format.

Example
-------
    from unit2_controller import Unit2


    def setup_unit2():
        # Create a Unit2 object, see example_config.yaml for an example configuration file
        unit2 = Unit2('config.yaml')
        unit2.connect()
        return unit2
        
        
    unit2 = setup_unit2()
    # Test the pump
    for name, pump in unit2.pump.items():
        pump = unit2.pump[name]
        
        if pump.move_liquid(millilitre=1.0, direction=1):
            print(f"moved 1 ml liquid in Pump {name} in direction 1")
        else:
            raise Exception(f"Failed to move liquid in Pump {name}")
        
        if pump.move_liquid_by_steps(steps=-48):
            print(f"moved liquid by 48 steps in Pump {name} in direction -1")
        else:
            raise Exception(f"Failed to move liquid by steps in Pump {name}")

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
            
    unit2.disconnect()

See Also
--------
unit2_controller.module.pump
unit2_controller.module.valve
"""

import yaml
from pathlib import Path
from isotope import Isotope
from isotope.utils.logging import setup_logger
from .module import Pump, Valve


class Unit2:
    """The Unit2 Class is for controlling the Nuclear Medicine Unit 2 modular system.
    
     """

    def __init__(self, config_file: str = "config.yaml"):
        """
        Args:
            config_file (str, optional): path to the YAML configuration file. See example_config.yaml for an example. Defaults to "config.yaml".
        """
        self._logger = setup_logger(__package__)
        self._logger.info("==============================================")
        self._logger.info(f"Unit2 Controller initiating...")
        self._logger.debug(f"Current working directory: {Path.cwd()}")
        
        self._logger.debug(f"Loading configuration from {config_file}...")
        self.config = yaml.load(open(config_file, 'r'), Loader=yaml.FullLoader)
        self._logger.info(f"Configuration loaded successfully.")

        self._isotopes: dict[int | str, Isotope] = {}
        try:
            self.initialise_isotope_board()
            self.pump = Pump(self._isotopes, self.config)
            self.valve = Valve(self._isotopes, self.config)
        except ValueError as e:
            self._logger.error("Failed to initialise Unit2 Controller.", exc_info=True)
            raise e
        self._logger.info("Unit2 Controller initiated successfully.")

    def initialise_isotope_board(self):
        """Initializes the isotope boards based on the configuration settings.
        """
        self._logger.debug(f"Initialising Isotope Breakout boards... {len(self.config['isotope_board']['devices'])} registered.")
        defaults = self.config['isotope_board']['defaults']
        for isot in self.config['isotope_board']['devices']:
            debug_enabled = isot.get('debug_enabled', defaults['debug_enabled'])
            comm_timeout = isot.get('comm_timeout', defaults['comm_timeout'])
            self._logger.debug(f"Initialising Isotope Breakout ${isot['name']}: \nPort: {isot['port']}, Debug: {debug_enabled}, Timeout: {comm_timeout}.")
            self._isotopes[isot['name']] = Isotope(isot['port'], debug_enabled, comm_timeout)
            self._logger.debug(f"Isotope Breakout {isot['name']} initialised successfully.")
            
    def connect(self):
        """Connect to the isotope boards.
        """       
        for name, isot in self._isotopes.items():
            self._logger.debug(f"Connecting to Isotope Breakout {name}...")
            isot.connect()
            self._logger.info(f"Isotope Breakout {name} connected.")
            
    def disconnect(self):
        """Disconnect the isotope boards.
        """
        for name, isot in self._isotopes.items():
            self._logger.debug(f"Disconnecting Isotope Breakout {name}...")
            isot.disconnect()
            self._logger.info(f"Isotope Breakout {name} disconnected.")
