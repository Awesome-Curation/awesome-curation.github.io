import os
import sys
import logging
import time
import datetime

FILE_NAME = '/data/sandbox'
WRITING   = '**** Writing '
FINISHED  = '**** Finished '
CATEGORY  = 'Category: '
FULL_LIST = 'List: '
SCRIPT    = 'Script: '
DEBUG_LVL = logging.INFO
path = os.path.dirname(__file__)
FILE_PATH = os.path.abspath(os.path.join(path, os.pardir)) + '/data/script_log'

class ContextFilter(logging.Filter):
    """ Injects contextual information into the log.

    Every log call is filtered in 'filter' to save and print 
    information throughout the script execution. 

        - TODO:
            * Subclass & separate responsibilities 
            * Add average times

    """
    def __init__(self):
        self.msgs = {}

    # Full script info
    _script_time = time.time()
    _script_lists = 0
    _script_categories = 0
    _script_repos = 0
    _errors = 0
    _warnings = 0

    # Awesome list execution time
    _list_time = _script_time

    # Category execution time
    _category_time = _script_time

    # Single repo execution time
    _repo_time = _script_time

    def _get_current_time(self):
        return time.time()
    
    def _get_elapsed_time(self, start):
        """ 
        Return Format: H:M:mS 
        """
        s = float('%0.4f' % (self._get_current_time() - start)) 
        t = datetime.timedelta(seconds=s)
        return str(t)

    def _critical_err(self, record):
        """ 
        Exit script with debug info when a Critical message is logged
        """
        self._print('')
        self._print('******************** CRITICAL ERROR **********************')
        self._print('File:     {}'.format(record.filename))
        self._print('Function: {}'.format(record.funcName))
        self._print('Message:  {}'.format(record.getMessage()))
        self._print('***********************************************************')
        self._end_script(record)
        sys.exit(1)
    
    def _begin_category(self, record):
        """ 
        Add a Category beginning marker to the logger & set the timer
        """
        try:
            list_name = record.args['Awesome List']
            category = record.args['Category']
        except (TypeError, KeyError):
            self._print('Unable to get category info')
            self._print(record.getMessage())
            record.msg = '**** Writing Unknown Category ****'
        else:
            record.msg = '**** Writing New Category [' + list_name + ']: ' + category + ' ****'
        self._category_time = self._get_current_time()
    
    def _begin_list(self, record):
        """ 
        Add a List beginning marker to the logger & set the timer
        """
        try:
            list_name = record.args['Awesome List']
        except (TypeError, KeyError):
            self._print('Unable to get list info')
            self._print(record.getMessage())
            record.msg = '**** Writing Unknown List ****'
        else:
            record.msg = '**** Writing New List: ' + list_name + ' ****'
        self._list_time = self._get_current_time()

    
    def _end_category(self, record):
        """
        Write Category statistics when section is complete   
        """
        self._print('=================== Category Statistics ===================')
        try:
            self._print('List:       {}'.format(record.args['Awesome List']))
            self._print('Category:   {}'.format(record.args['Category']))
            self._print('File Name:  {}'.format(record.args['File Name']))
            self._print('Repo Count: {}'.format(str(record.args['Repo Count'])))
        except (TypeError, KeyError):
            self._print('Unable to get category info')
            self._print(record.getMessage())
        self._print('Time:       {}'.format(self._get_elapsed_time(self._category_time)))
        self._print('===========================================================')
    
    def _end_list(self, record):
        """
        Write List statistics when finished
        """
        self._print('================= Awesome List Statistics =================')
        try:
            self._print('List:           {}'.format(record.args['Awesome List']))
            self._print('Category Count: {}'.format(record.args['Category Count']))
            self._print('Repo Count:     {}'.format(record.args['Repo Count']))

            self._script_repos += record.args['Repo Count'] 
            self._script_categories += record.args['Category Count']
        except (TypeError, KeyError):
            self._print('Unable to get category info')
            self._print(record.getMessage())
        self._print('Time:           {}'.format(self._get_elapsed_time(self._list_time)))
        self._print('===========================================================')

    def _end_script(self, record):
        """
        Write final script statistics
        """
        self._print('==================== Script Statistics ====================')
        try:
            self._print('List Count:     {}'.format(self._script_lists))
            self._print('Category Count: {}'.format(self._script_categories))
            self._print('Repo Count:     {}'.format(self._script_repos))
            self._print('Warnings:       {}'.format(self._warnings))
            self._print('Errors:         {}'.format(self._errors))
        except (TypeError, KeyError):
            self._print('Unable to get category info')
            self._print(record.getMessage())
        self._print('Time:           {}'.format(self._get_elapsed_time(self._script_time)))
        self._print('===========================================================')
    
    def _print(self, text):
        """ 
        Print to console and log file
        """
        print(text)
        with open(FILE_PATH, 'a') as f:
            t = text + '\n' if text else 'NoneType\n'
            f.write(t)

    def filter(self, record):
        """ Filter every logging call

        This function filters logging calls by checking if markers (global constants) 
        are found to inject contextual info and keep statistics throughout the script 
        execution. Critical messages will abort the script.

        Args:
            record (logging.LogRecord): This object contains all info pertinent to the 
                                        event being logged.
                - Key Value pairs (**kwargs) are held in the 'args' attribute
                  and used to pass in extra information at the markers 

        Returns:
            bool: Print the messages passed to the logger (else don't)

        """
        if record.levelno == logging.CRITICAL:
            self._critical_err(record)
        elif record.levelno == logging.ERROR:
            self._errors += 1
        elif record.levelno == logging.WARNING:
            self._warnings += 1
        
        msg = record.getMessage()

        if WRITING in msg:
            if CATEGORY in msg:
                self._begin_category(record)
            elif FULL_LIST in msg:
                self._begin_list(record)
        
        if FINISHED in msg:
            if CATEGORY in msg:
                self._end_category(record)
            elif FULL_LIST in msg:
                self._end_list(record)
            elif SCRIPT in msg:
                self._end_script(record)
            return False
            
        return True

def setup_logging():
    """ Setup the logging instance for the script

    This function will set up a logger to print all levels of messages to
    FILE_PATH and a simplified console logger to print DEBUG_LVL level 
    messages to the console. 
    """
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s.%(msecs)03d %(funcName)-19s %(levelname)-8s %(message)s',
                        datefmt='%H:%M:%S',
                        filename=FILE_PATH,
                        filemode='w')

    # Simplified log for console
    console = logging.StreamHandler()
    console.setLevel(DEBUG_LVL)

    formatter = logging.Formatter('%(name)-6s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)

    filter = ContextFilter()
    logging.getLogger('').addHandler(console)
    logging.getLogger('').addFilter(filter)

def set_console_level(lvl):
    """ Edit the debugging level of the console logger

    This function sets the logging level to avoid manually
    setting the DEBUG_LVL global variable.

        - TODO:
            * Currently doesn't work. Can't set the level
              here for some reason.
    """
    if 'Debug' in lvl:
        logging.getLogger('').setLevel(logging.DEBUG)

def add_logger(name):
    """ Create a new logger instance

    This function adds a new logger to the script with the same 
    attributes as the root logger.

    Args:
        name (str): Name of the logger
    """
    if not isinstance(name, str):
        logging.critical("Unable to build new log. Invalid argument")

    filter = ContextFilter()
    logger = logging.getLogger(name) 
    logger.addFilter(filter)
    return logger

'''
# Subclass testing
class StatsLogger(ContextFilter):
    def filter(self, record):
        if record.levelno == logging.ERROR:
            super(StateLogger, self).final_statistics()
            return True
        return super(StateLogger, self).filter(record)
'''
