import logging
from menu_view import View
from Queue import Queue
import threading

class Menu(object):

    logger = logging.getLogger('main')
 
    def __init__(self, control, parent):
        self.view = View(parent)
                    
