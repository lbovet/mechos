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
