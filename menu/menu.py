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

import logging
from menu_view import View
from Queue import Queue
import threading

class Menu(object):

    nodes = { "Music": None, "Radio" : { "Lolo": { "Couleur3" : None}, "Sarah": { "RSR La 1ere":None, "Soma FM": None}}, "Photos": { "Turquie": None, "Grece":None }}

    logger = logging.getLogger('main')
 
    def __init__(self, control, parent):
        self.view = View(parent)
        self.view.set_node_provider(self.get_node)
        
        import pickle
        import pickle
        f = open("music.pickle", "r")
        m = pickle.load(f)
        self.nodes['Music'] = m
        
    def get_node(self, path=[]):
        cursor = self.nodes
        for p in path:
            if type(cursor) == dict:
                if p < len(cursor.keys()):
                    cursor = cursor[cursor.keys()[p]]
                else:
                    return cursor.keys()
            else:
                return None
        if cursor and len(cursor) > 0:
            return cursor.keys()