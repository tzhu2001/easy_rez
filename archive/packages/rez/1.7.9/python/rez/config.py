import logging, os, re

LOGGER = None

def get_logger():
    global LOGGER
    
    if LOGGER==None:
        LOGGER = logging
    
    logging.getLogger().setLevel(10)
    return LOGGER


def get_bin_root():
    return os.environ.get('PRODTOOLS') + '/packages/rez/current/bin'

def window_path(path):
    if path.startswith('/'):
        path = re.sub('/([a-z|A-Z])/', '\g<1>:/', path)
        
    return path
    
    
def posix_path(path):
    if path.startswith('/'):
        path = re.sub('([A-Z|a-z])\:[/|\\\]', '/\g<1>/', path)
        
    return path