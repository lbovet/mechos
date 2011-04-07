#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk
import logging
import sys
import optparse
import gobject

from control import control
from menu import menu

gobject.threads_init()
gtk.gdk.threads_init()

class Main(object):

    logger = logging.getLogger('main')

    def __init__(self):        

        # Options and logging
        opt_parser = optparse.OptionParser()
        opt_parser.add_option("-d", "--debug", action="store_true", dest="debug", help="Issues all debug messages on the console.")        
        (options, args) = opt_parser.parse_args()

        formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

        if options.debug:
            level=logging.DEBUG
        else:
            level=logging.ERROR
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)

        logging.getLogger().setLevel(level)
        
        # Create window
        gtk.rc_parse('gtkrc')
        window = gtk.Window(gtk.WINDOW_POPUP)
        
        width = 240
        height = 320
        
        window.set_default_size(width, height)
        window.connect("destroy", self.destroy)
        
        main_box = gtk.Fixed()
        window.add(main_box)
        
        # Create application components
        
        control_height = 48
        
        control_box = gtk.Fixed()
        control_box.set_size_request(width, control_height)
        main_box.put(control_box, 0, height-control_height)        
        control.Control(control_box)        
        control_box.show()
        
        menu_box = gtk.Fixed()
        menu_box.set_size_request(width, height-control_height)
        main_box.put(menu_box, 0, 0)        
        menu.Menu(control, menu_box)        
        menu_box.show()
        
        # Main loop
        main_box.show()
        window.show()
        try:
            gtk.gdk.threads_enter()
            gtk.main()
            gtk.gdk.threads_leave()
        except:
            sys.exit()

    def destroy(self):
        self.logger.debug("Close requested")
        gtk.main.quit()

Main()
