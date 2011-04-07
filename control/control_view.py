import gtk
import logging

class View(object):

    logger = logging.getLogger("control.view")

    def __init__(self, parent):
        frame = gtk.Frame("Control")
        frame.set_size_request(*parent.get_size_request())
        parent.add(frame)
        frame.show()
        self.logger.debug("init");
