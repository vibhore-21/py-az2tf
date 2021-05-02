import logging
import sys
import os

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def get_logger(log_level="DEBUG", logger_name="az2tf", log_to_console=True):
    # setup handler for the logger
    print("PROJECT DIR {}".format(PROJECT_DIR))
    logger = logging.getLogger(logger_name)
    log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger.setLevel(log_level)
    log_path = os.path.join(PROJECT_DIR, 'logs/{}.log'.format(logger_name))
    fh = logging.FileHandler(log_path)
    fh.setFormatter(log_formatter)
    logger.addHandler(fh)
    if log_to_console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(log_formatter)
        logger.addHandler(ch)

    return logger


def get_tf_state_rm_file_path(resource_name, suffix="-1", resource_group=''):
    return resource_name + "-staterm" + suffix + ".sh"


def get_tf_import_state_script_path(resource_name, suffix='-1', resource_group=''):
    return resource_name + "-stateimp" + suffix + ".sh"


# logger = get_logger(logger_name="test")
