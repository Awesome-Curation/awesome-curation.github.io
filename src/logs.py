import logging
import time

class ContextFilter(logging.Filter):
    """ Injects contextual information into the log.

    Every log call is filtered in 'filter' to save and print 
    information throughout the script execution. 

        - TODO:
            * Subclass & separate responsibilities 

    """
    def __init__(self):
        self.msgs = {}

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

    def _get_current_time(self):
        return time.time()
    
    def _get_elapsed_time(self, start):
        return str(float('%0.4f' % (self._get_current_time() - start)))

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
        msg = record.getMessage()
        #if self._repos_complete % 2 ==0:
        #    self._end_logging()
        
        if 'love' in record.getMessage():
            #print("gots love")
            # Cant set message when parameters are used
            # use TypeError - not all arguments converted during string formatting
            #record.msg = "zzzzz"
            pass
            #self.formatter.format(record) 
        
        return True

def setup_logging():
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d %(funcName)-19s %(levelname)-8s %(message)s',
                    datefmt='%H:%M:%S',
                    filename='data/sandbox',
                    filemode='w')

    # Simplified log for console
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(name)-6s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)

    filter = ContextFilter()
    logging.getLogger('').addHandler(console)
    logging.getLogger('').addFilter(filter)

def set_console_level(lvl):
    if 'Debug' in lvl:
        logging.getLogger('').setLevel(logging.DEBUG)

def add_logger(name):
    if not isinstance(name, str):
        logging.critical("Unable to build new log. Invalid argument")

    filter = ContextFilter()
    logger = logging.getLogger(name) 
    logger.addFilter(filter)
    return logger

setup_logging()