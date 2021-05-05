import logging
import sys
import os

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# todo: read these globals from settings/config
CLUB_CONFIG = True
GROUP_BY_RG = True

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


def get_tf_state_rm_file_path(resource_type, prefix, resource_group):
    path = prefix + resource_type + "-staterm.sh"
    if resource_group and GROUP_BY_RG:
        return resource_group + '/' + path
    return path


def get_tf_import_state_script_path(resource_type, prefix, resource_group):
    path = prefix + resource_type + "-stateimp.sh"
    if resource_group and GROUP_BY_RG:
        return resource_group + "/" + path
    return path


def get_tf_config_file_path(resource_type, rg, name, scope=''):
    path = ''
    if CLUB_CONFIG:
        path = resource_type + '.tf'
        if GROUP_BY_RG:
            path = rg + '/' + path
    elif scope:
        path = resource_type + '__' + rg + '__' + name + '__' + scope + '.tf'
    return path


def get_tf_compatible_name(name):
    tf_name = name.replace(".", "-").replace("[", "-").replace("]", "-").replace(" ", "_")

    # try:
    #    rname=rname.encode('utf-8', 'ignore')
    # except UnicodeDecodeError:
    #    print('Problem with the name of this item: '+name)
    #    print('Please rename this item in the Azure Portal')
    #    rname=str(uuid.uuid4())
    #    #rname=rname.encode('utf-8', 'ignore')

    return tf_name


def get_tf_compatible_rg(value):
    tf_rg = value.replace(".", "-").lower()
    if tf_rg[0].isdigit():
        tf_rg = "rg_" + tf_rg
    return tf_rg
