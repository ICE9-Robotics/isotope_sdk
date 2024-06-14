import yaml
import isotope
from .module import Pump, Valve


class Unit2:
    """
    The Unit2 Class.

    Attributes:
        pump (Pump): pumps connected to the Isotope boards.
        valve (Valve): valves connected to the Isotope boards.
        _isotope_boards (dict[int, isotope.Isotope_comms_protocol]): communication protocol for installed isotope boards.
    """

    pump: Pump
    valve: Valve
    _isotope_boards: dict[int, isotope.Isotope_comms_protocol]

    def __init__(self, config_file: str = "config.yaml"):
        self.config = yaml.load(open(config_file, 'r'), Loader=yaml.FullLoader)

        self.pump = Pump(self._isotope_boards, self.config())
        self.valve = Valve(self._isotope_boards, self.config())

    def initialise_isotope_board(self):
        """
        Initializes the isotope boards based on the configuration settings.
        """
        defaults = self.config['isotope_board']['defaults']
        for board in self.config['isotope_board']:
            debug_enabled = board.get('debug_enabled', defaults['debug_enabled'])
            comm_timeout = board.get('comm_timeout', defaults['comm_timeout'])
            self._isotope_boards[board['id']] = isotope.Isotope_comms_protocol(board['port'], debug_enabled, comm_timeout)
            
    def close_connection(self):
        """
        Closes the connection to the isotope boards.
        """
        for board in self._isotope_boards.values():
            board.close()
