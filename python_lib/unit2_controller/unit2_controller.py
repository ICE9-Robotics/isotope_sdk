import yaml
from isotope import Isotope
from .module import Pump, Valve


class Unit2:
    """
    The Unit2 Class.

    Attributes:
        pump (Pump): pumps connected to the Isotope boards.
        valve (Valve): valves connected to the Isotope boards.
        _isotopes (dict[int, isotope.Isotope_comms_protocol]): communication protocol for installed isotope boards.
    """

    pump: Pump
    valve: Valve
    _isotopes: dict[int, Isotope]

    def __init__(self, config_file: str = "config.yaml"):
        self.config = yaml.load(open(config_file, 'r'), Loader=yaml.FullLoader)
        self.initialise_isotope_board()
        self.pump = Pump(self._isotopes, self.config)
        self.valve = Valve(self._isotopes, self.config)

    def initialise_isotope_board(self):
        """Initializes the isotope boards based on the configuration settings.
        """
        self._isotopes = {}
        defaults = self.config['isotope_board']['defaults']
        for isot in self.config['isotope_board']['devices']:
            debug_enabled = isot.get('debug_enabled', defaults['debug_enabled'])
            comm_timeout = isot.get('comm_timeout', defaults['comm_timeout'])
            self._isotopes[isot['id']] = Isotope(isot['port'], debug_enabled, comm_timeout)
            
    def connect(self):
        """Connect to the isotope boards.
        """       
        for isot in self._isotopes.values():
            self._isotopes[isot['id']].connect()
            
    def disconnect(self):
        """
        Disconnect the isotope boards.
        """
        for isot in self._isotopes.values():
            isot.disconnect()
