import yaml
from pathlib import Path
from typing import Union
from isotope import Isotope
from isotope.utils.logging import setup_logger
from .module import Pump, Valve


class Unit2:
    """
    The Unit2 Class is for controlling the Nuclear Medicine Unit 2 modular system.
    It provides a straightforward interface for controlling the pumps and valves connected to multiple Isotope boards.
    Details of the pumps, valves, and Isotope boards can be specified in a configuration file in YAML format.

    Attributes:
        pump (Pump): an instance of the Pump class, providing methods for communicating with the pumps connected to the Isotope boards.
        valve (Valve): an instance of the Valve class, providing methods for communicating with the valves connected to the Isotope boards.
        _isotopes (dict[[int | str], isotope.Isotope_comms_protocol]): communication protocol instances for installed isotope boards.
    """

    pump: Pump
    valve: Valve
    _isotopes: dict[Union[int, str], Isotope]

    def __init__(self, config_file: str = "config.yaml"):
        """The constructor for the Unit2 class.

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

        self.initialise_isotope_board()
        self.pump = Pump(self._isotopes, self.config)
        self.valve = Valve(self._isotopes, self.config)
        self._logger.info("Unit2 Controller initiated successfully.")

    def initialise_isotope_board(self):
        """Initializes the isotope boards based on the configuration settings.
        """
        self._logger.debug(f"Initialising Isotope Breakout boards... Registered ${len(self.config['isotope_board']['devices'])}.")
        self._isotopes = {}
        defaults = self.config['isotope_board']['defaults']
        for isot in self.config['isotope_board']['devices']:
            debug_enabled = isot.get('debug_enabled', defaults['debug_enabled'])
            comm_timeout = isot.get('comm_timeout', defaults['comm_timeout'])
            self._logger.debug(f"Initialising Isotope Breakout ${isot['name']}: \nPort: {isot['port']}, Debug: {debug_enabled}, Timeout: {comm_timeout}.")
            self._isotopes[isot['name']] = Isotope(isot['port'], debug_enabled, comm_timeout)
            self._logger.debug(f"Isotope Breakout ${isot['name']} initialised successfully.")
            
    def connect(self):
        """Connect to the isotope boards.
        """       
        for name, isot in self._isotopes.items():
            self._logger.debug(f"Connecting to Isotope Breakout ${name}...")
            isot.connect()
            self._logger.info(f"Isotope Breakout ${name} connected.")
            
    def disconnect(self):
        """Disconnect the isotope boards.
        """
        for name, isot in self._isotopes.items():
            self._logger.debug(f"Disconnecting Isotope Breakout ${name}...")
            isot.disconnect()
            self._logger.info(f"Isotope Breakout ${name} disconnected.")
