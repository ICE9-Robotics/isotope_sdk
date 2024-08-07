"""Contains `PumpObj` and `Pump` classes, used to control peristaltic pumps connected to the Isotope board MOT ports.

`PumpObj` class inherits from the `unit2_controller.module.device.DeviceObj` class containing the actual implementation of functions to control the pumps. 
`Pump` class inherits from the `unit2_controller.module.device.Device` class that initialises and manages the `PumpObj` instances for all registered pumps.

Notes
-----
Users are encouraged to use the `unit2_controller.unit2_controller.Unit2` class to access the pumps instead of creating their own instances of these 
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
    # Test the pump
    for name, pump in unit2.pump.items():
        pump = unit2.pump[name]
        
        if pump.move_liquid(millilitre=1.0, direction=1):
            print(f"Pump {name} is now moving liquid by 1 ml in direction 1")
            pump.wait_until_completed()
            print(f"Pump {name} is done.")
        else:
            raise Exception(f"Failed to move liquid in Pump {name}")
        
        if pump.move_liquid_by_steps(steps=-48):
            print(f"Pump {name} is now moving 48 steps in direction -1")
            pump.wait_until_completed()
            print(f"Pump {name} is done.")
        else:
            raise Exception(f"Failed to move liquid by steps in Pump {name}")

        pump.power_off()
        

See Also
--------
unit2_controller.unit2_controller.Unit2
unit2_controller.module.device
"""

import isotope
from .device import Device, DeviceObj, DeviceError


class PumpObj(DeviceObj):
    """The PumpObj class provides methods for controlling peristaltic pumps connected to the Isotope board MOT ports.
    """

    def __init__(self) -> None:
        super().__init__()
        self.rpm = 0
        self.current = 0
        self.steps_per_degree = 0
        self.steps_per_ml = 0
        self.default_dir = 0
        self._initialised = False

    def initialise(self, isotope_board: isotope.Isotope, port_id: int) -> None:
        """Initializes the pump object with the specified board and port ID.

        Args:
            isotope_board (isotope.Isotope): The Isotope object.
            port_id (int): The ID of the port to which the pump is connected.
        """
        self._logger.debug(f"Initialising Pump connected to Isotope Breakout {isotope_board} on port {port_id}...")

        self.motor = isotope_board.motors[port_id]
        self.motor.configure(self.steps_per_degree, self.current, self.rpm)
        self._initialised = True

    def move_liquid_by_steps(self, steps: int) -> bool:
        """Moves liquid by rotating the pump motor with the specified number of steps.

        Args:
            steps (int): The number of steps to rotate the pump motor. Can be negative to reverse the direction.

        Returns:
            bool: True if the execution is successful, False otherwise.
        """
        self._logger.debug(f"Moving liquid by {steps} steps...")
        assert self._initialised, "Pump not initialised."
        if not self._is_powered():
            self.motor.enable()
        result = self.motor.rotate_by_steps(steps * self.default_dir)
        self._logger.debug(f"{'Command was received' if result else 'Failed to deliver command'}.")
        return result

    def move_liquid(self, millilitre: float, direction: int) -> bool:
        """Moves the specified amount of liquid in milliliters.

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
    
    def is_completed(self) -> bool:
        """Checks if the pump has finished pumping liquid.

        Returns:
            bool: True if the pump has finished moving liquid, False otherwise.
        """
        return self.motor.is_motion_completed()
    
    def wait_until_completed(self) -> None:
        """Waits until the pump has finished pumping liquid.
        """
        self.motor.wait_until_motion_completed()
        
    def power_off(self) -> bool:
        """Turns off the motor.

        Returns:
            bool: True if the motor is successfully turned off, False otherwise.
        """
        self._logger.debug("Powering off pump...")
        return self.motor.disable()
    
    def power_on(self) -> bool:
        """Turns on the motor.
        Note: The motor is turned on automatically when it is commanded to move. 
        You may turn on the motor purposely for holding the torsion.

        Returns:
            bool: True if the motor is successfully turned on, False otherwise.
        """
        self._logger.debug("Powering on pump...")
        return self.motor.enable()

    def _is_powered(self) -> bool:
        """Checks if the motor is powered.

        Returns:
            bool: True if the motor is powered, False otherwise.
        """
        return self.motor.is_enabled()


class Pump(Device[PumpObj]):
    """The Pump class initialises and manages the `PumpObj` instances.
    """

    def __init__(self, isotope_boards: dict[int | str, isotope.Isotope], config: dict):
        """
        Args:
            isotope_boards (dict[int | str, isotope.Isotope]): `isotope.Isotope` instances of the installed Isotope boards.
            config (dict): A dictionary containing the configuration settings for the pumps.
        """
        super().__init__(isotope_boards, config['pump'])
        self._logger.debug("Initialising Pump...")
        self._configure()
        self._logger.debug("Pump initialised.")

    def _configure(self):
        """Configures pumps based on the provided configuration settings.
        """
        self._logger.debug(f"Configuring pumps... ${len(self._config['devices'])} registered.")

        defaults = self._config['defaults']
        self._devices = {}
        for device in self._config['devices']:
            self._logger.debug(f"Configuring Pump ${device['name']}...")

            board_name = device['board_name']
            if board_name not in self._isots.keys():
                raise ValueError(
                    f"Isotope board {board_name} is not registered. Have you assigned the correct board_name to pump {device['name']} in the config file?")
            port_id = device['port_id']
            if port_id >= len(self._isots[board_name].motors):
                raise ValueError(f"Port ID {port_id} is out of range.")
            if port_id < 0:
                raise ValueError(f"Port ID {port_id} is invalid. Port ID must be greater than or equal to 0.")

            pump = PumpObj()
            pump.rpm = device.get('rpm', defaults['rpm'])
            pump.current = device.get('current', defaults['current'])
            pump.steps_per_degree = device.get('steps_per_degree', defaults['steps_per_degree'])
            pump.steps_per_ml = device.get('steps_per_ml', defaults['steps_per_ml'])
            pump.default_dir = -1 if device.get('reverse_direction', defaults['reverse_direction']) else 1
            pump.initialise(self._isots[board_name], port_id)
            self._devices[device['name']] = pump
            self._logger.debug(f"Pump ${device['name']} configured.")
