import logging
from typing import Union
import isotope

class DeviceObj:
    pass

class Device:
    """
    The Device class is an abstract class for initialising and managing the inheritance of DeviceObj
    """
    
    _config: dict[str, any]
    _isots: tuple[isotope.Isotope,...]
    _devices: dict[Union[int, str], DeviceObj]
    
    def __init__(self, isotope_boards: tuple[isotope.Isotope,...], config: dict):
        """
        Constructor for the Device class.
        
        Args:
            isotope_boards (tuple[isotope.Isotope,...]): Isotope instances of the installed Isotope boards.
            config (dict): A dictionary containing the configuration settings for the devices.
        """
        self._logger = logging.getLogger(__package__)
        self._isots = isotope_boards
        self._config = config
    
    def names(self) -> list[Union[int, str]]:
        """
        Gets the names of all the devices.
        
        Returns:
            list[[int | str]]: A list of device names.
        """
        return list(self._devices.keys())
    
    def items(self) -> list[tuple[Union[int, str], DeviceObj]]:
        """
        Provides a view of the content in the form of name-value sets.
        
        Returns:
            list[tuple[int | str, PumpObj]]: A list of name-value sets.
        """
        return self._devices.items()
    
    def __getitem__(self, name: Union[int, str]) -> DeviceObj:
        """
        Gets the device object with the specified name.
        
        Args:
            name ([int | str]): The name of the device.
        
        Returns:
            DeviceObj: The device object.
        """
        self._verify_name(name)
        return self._devices[name]
    
    def _verify_name(self, name: Union[int, str]) -> None:
            """
            Verifies if a device with the given name exists.

            Args:
                name ([int | str]): The name of the device to verify.

            Raises:
                ValueError: If the device with the given name is not found.
            """
            if name not in self._devices:
                raise ValueError(f"Device with name {name} not found.")