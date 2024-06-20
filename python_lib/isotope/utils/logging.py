import logging
from logging.handlers import RotatingFileHandler
from typing import Union
import os


def setup_logger(name: str = 'isotope', 
                 screen_level : Union[int, None] = logging.WARN, 
                 file_level: Union[int, None] = logging.DEBUG, 
                 log_file: Union[int, None] = None) -> logging.Logger:
    """Setup logger for the package.

    Args:
        name (str, optional): Name of the logger to use. Defaults to 'isotope'.
        screen_level ([int | None], optional): level of logging to be displayed in the terminal. Set to None to disable. Defaults to logging.WARN.
        file_level ([int | None], optional): level of logging to be logged in file. Set to None to disable. Defaults to logging.DEBUG.
        log_file ([int | None], optional): name of the file. Defaults to the name of the logger.
    """

    logger = logging.getLogger(name)
    
    try:
        if logger.configured:
            return logger
    except AttributeError:
        pass
    
    logger.setLevel(min(screen_level, file_level))

    # Stream handler
    if screen_level is not None:
        s_handler = logging.StreamHandler()
        s_handler.setLevel(screen_level)
        s_format = logging.Formatter('%(name)s::%(module)s::%(levelname)-8s: %(message)s')
        s_handler.setFormatter(s_format)
        logger.addHandler(s_handler)

    # File handler
    if file_level is not None:
        if log_file is None:
            log_file = os.path.join('.log',f'{name}.log')
        if not os.path.exists(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file))
        f_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=10)
        f_handler.setLevel(file_level)
        f_format = logging.Formatter('%(asctime)s %(name)s::%(module)s::%(levelname)-8s: %(message)s')
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)

    logger.configured = True
    return logger
