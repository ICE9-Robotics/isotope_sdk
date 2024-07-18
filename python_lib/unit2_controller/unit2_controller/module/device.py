"""Contains abstract classes for other submodules that represents different devices to be controlled by the Isotope Breakout board.

`DeviceObj` class is the actual implementation of the device, while the `Device` class is a container for multiple `DeviceObj` instances and handles initialisation
of each DeviceObj instance.

Notes for developers
--------------------
For each device that needs to be controlled by the Isotope board, a new module should be created in the `module` super-module. The new module should 
contain two classes: one to inherit from `DeviceObj` and the other from `Device`. 

The inheritant of `DeviceObj` should implement functions of the device that requires communicating with the Isotope board, such as initialises the initial states, 
uploading control parameters, executing a control commands, and reading the sensor values, etc.
The inheritant of `Device` should contain functions to initialise the properties or parameters of the device that does not require immediate communication with 
the Isotope board.

See Also
--------
unit2_controller.module.pump
unit2_controller.module.valve
"""

import logging
from typing import Generic, TypeVar
import isotope

class DeviceError(Exception):
    """A custom exception class for device-related errors.
    """
    pass


class DeviceObj:
    """The DeviceObj class is an abstract class for different devices that is to be controlled by the Isotope Breakout boards.
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger(__package__)


T = TypeVar("T", bound=DeviceObj)


class Device(Generic[T]):
    """The Device class is an abstract class for initialising and managing the inheritance of DeviceObj
    """

    def __init__(self, isotope_boards: tuple[isotope.Isotope, ...], config: dict[str, any]):
        """
        Args:
            isotope_boards (tuple[isotope.Isotope,...]): `isotope.Isotope` instances of the installed Isotope boards.
            config (dict[str, any]): A dictionary containing the configuration settings for the devices.
            
        Notes for developers
        --------------------
        In the derived classes, do not pass the full `config` to the constructor. Instead, pass the relevant part of the configuration, e.g. `config['pump']` or `config['valve']`.
        """
        self._logger = logging.getLogger(__package__)
        self._isots = isotope_boards
        self._config = config
        self._devices: dict[int | str, T] = {}

    def keys(self) -> list[int | str]:
        """
        Gets the names of all the devices.

        Returns:
            list[[int | str]]: A list of device names.
        """
        return list(self._devices.keys())

    def items(self) -> list[tuple[int | str, DeviceObj]]:
        """
        Provides a view of the content in the form of [[name,value], ..].

        Returns:
            list[tuple[int | str, PumpObj]]: A list of name-value sets.
        """
        return self._devices.items()

    def __getitem__(self, name: int | str) -> DeviceObj:
        """
        Gets the device object with the specified name.

        Args:
            name ([int | str]): The name of the device.

        Returns:
            DeviceObj: The device object.
        """
        self._verify_name(name)
        return self._devices[name]

    def _verify_name(self, name: int | str) -> None:
        """
        Verifies if a device with the given name exists.

        Args:
            name ([int | str]): The name of the device to verify.

        Raises:
            ValueError: If the device with the given name is not found.
        """
        if name not in self._devices:
            raise KeyError(f"Device with name {name} not found.")
