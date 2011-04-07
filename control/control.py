import logging
from control_view import View

class Control(object):

    logger = logging.getLogger('control')

    def __init__(self, parent):
        self.view = View(parent)
