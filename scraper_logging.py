import logging
from datetime import datetime
import pathlib



def create_logger():
    """
    Creates a logging object and returns it
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # create the logging file handler
    script_location = pathlib.Path().absolute()
    date_time = datetime.now()
    date_time = datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M-%S')
    fh = logging.FileHandler(f"{script_location}\\scraper_log_{date_time}.log")
    fmt = '\n\
**********************************************\n\
%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(fh)
    return logger



class LoggingDict():
    logging_dict = {}
    
    def __init__(self, **kwargs):
        self.logging_dict.update(kwargs)

    def __getitem__(self, key):
        return self.logging_dict[key]