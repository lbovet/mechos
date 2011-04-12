#!/usr/bin/python

## Copyright 2011 Laurent Bovet <laurent.bovet@windmaster.ch>
##
##  This file is part of Mechos
##
##  Mechos is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pygtk
pygtk.require('2.0')
import gtk
import logging
import sys
import optparse
import gobject

from control import control
from menu import menu

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
        gtk.rc_add_default_file('gtkrc')
        window = gtk.Window()
        
        width = 240
        height = 320
        
        window.set_default_size(width, height)
        window.connect("destroy", self.destroy)
        
        main_box = gtk.Fixed()
        window.add(main_box)
        
        # Create application components
        
        control_height = 0
        
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
        if window.get_screen().get_width() < 400:
            window.fullscreen()
        try:
            gtk.main()
        except:
            sys.exit()

    def destroy(self, event):
        self.logger.debug("Close requested")
        sys.exit()

Main()
