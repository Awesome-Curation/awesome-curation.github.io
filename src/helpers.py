#!/usr/bin/env python
# -*- coding: utf-8 -*

# Standard libs
import os.path
import re
import json
import logging
import time

# Custom
import api

class ContextFilter(logging.Filter):
    """ Injects contextual information into the log.

    Every log call is filtered in 'filter' to save and print 
    information throughout the script execution. 

        - TODO:
            * Subclass & separate responsibilities 

    """
    def __init__(self, formatter):
        self.msgs = {}
        self.formatter = formatter

    # Full script info
    _script_time = time.time()
    _script_lists = 0
    _script_categories = 0
    _script_repos = 0

    # Awesome list info
    _list_time = _script_time
    _list_categories = 0
    _list_repos = 0

    # Get category info
    _category_time = _script_time
    _category_repos = 0

    # Get single repo info
    _repo_time = _script_time

    def _get_current_time():
        return time.time()
    
    def _get_elapsed_time(start):
        return _get_current_time() - start

    def _end_logging(self):
        print('='*40)
        print('Logging ended with count: ' + str(self._repos_complete))
        elapsed_time = time.time() - self._start_time
        print("TOTAL TIME:")
        print('Time elapsed: ' + str(float("%0.4f" % (elapsed_time))))
        print('='*40)
        self._start_time = time.time()
    
    def _critical_err(self):
        print('='*40)
        print('Logging ended with count: ' + str(self._repos_complete))
        elapsed_time = time.time() - self._start_time
        print("TOTAL TIME:")
        print('Time elapsed: ' + str(float("%0.4f" % (elapsed_time))))
        print('='*40)

    def filter(self, record):
        self._repos_complete += 1
        #if self._repos_complete % 2 ==0:
        #    self._end_logging()
        
        if 'love' in record.getMessage():
            #print("gots love")
            record.msg = "zzzzz"
            #self.formatter.format(record) 
        
        return True

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d %(funcName)-12s %(levelname)-8s %(message)s',
                    datefmt='%H:%M:%S',
                    filename='data/sandbox',
                    filemode='w')

# Simplified log for console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
filter = ContextFilter(formatter)
logging.getLogger('').addHandler(console)
logging.getLogger('').addFilter(filter)
logging.getLogger('core').addHandler(console)
logging.getLogger('core').addFilter(filter)
logging.getLogger('api').addHandler(console)
logging.getLogger('api').addFilter(filter)


# Now, we can log to the root logger, or any other logger. First the root...
logging.info('Jackdaws love my big sphinx of quartz. %s', 'hell')
logging.info('32eJackdaws love my big sphinx of quartz.')
logging.info('sdcsadJackdaws love my big sphinx of quartz.')
logging.info('454gfvJackdaws love my big sphinx of quartz.')
logging.info('opmmJackdaws love my big sphinx of quartz.')

# Now, define a couple of other loggers which might represent areas in your
# application:

logger1 = logging.getLogger('myapp.area1')
logger2 = logging.getLogger('myapp.area2')

logger1.debug('Quick zephyrs blow, vexing daft Jim.')
logger1.info('How quickly daft jumping zebras vex.')
logger2.warning('Jail zesty vixen who grabbed pay from quack.')
logger2.error('The five boxing wizards jump quickly.')




def get_valid_filename(name):
    """ Get a valid filename for a string

    This function converts string into a valid filename
    to store data. Should also be used on button actions
    when fetching the file.

    Args:
        name (str): string to convert
    Returns:
        str: valid filename
    
    """
    s = str(name).strip().replace(' ', '_')
    return re.sub('(?u)[^-\w.]', '', s)

def get_root_path(f=__file__):
    """ Get the root path of the project

    - TODO:
        * Probably a much better way

    Args:
        f (str): filename
    Returns:
        str: absolute root path of the project

    """
    path = os.path.dirname(f)
    return os.path.abspath(os.path.join(path, os.pardir))

# Write data/emojis.txt file with GitHub assets links
# Return the dictionary to caller if needed
def write_emojis():
    """ Write GitHub emoji image assets to file

    This functions retrieves the asset links from the API
    as a json dictionary and pretty print them a file. Ideally
    this should only be called once and the file is used for
    all retrieval after. Can be called again in the event of
    a file reading failure.

    Returns:
        dict (optional): json emoji names & asset links

    """
    path = get_root_path()
    g_emojis = api.get_emojis()

    # Pretty print to file
    style = json.dumps(g_emojis, indent=4, sort_keys=True)
    with open(path + '/data/emojis.txt', 'w') as f:
        f.write(style)

    return g_emojis

def console_print(repo, url, data):
    """ Print repository data to console

    - TODO:
        * Use a logging function instead to catch all
          exceptions 

    Args:
        repo (str): repository name
        urls (str): repository link
        data (dict): json repository response data

    """
    stars = data['stargazers_count']
    forks = data['forks_count']
    lang = data['language']
    print('='*60)
    print('Repo:     ' + repo)
    print('Link:     ' + url)
    print('Stars:    ' + str(stars))
    print('Forks:    ' + str(forks))
    print('Language: ' + str(lang))    
    print('='*60+'\n')

