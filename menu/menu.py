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
        f = open("music.pickle", "r")
        m = pickle.load(f)
        #m = {"Playas Gon' Play" : None,
                #"Where My Girls At" : None,
                #"Are You Feelin' Me" : None,
                #"Are You That Somebody" : None,
                #"I Don't Wanna" : None,
                #"More Than A Woman" : None,
                #"Try Again" : None,
                #"Try Again Remix" : None,
                #"Try Again (No No No Remix)" : None,
                #"Come Back In One Piece" : None,
                #"Brotha Remix (Angie Stone & Eve)" : None,
                #"I Paid My Dues" : None,
                #"I'm Outta Love" : None,
                #"All Or Nothing" : None,
                #"Shining Star" : None,
                #"Who Let The Dogs Out ?" : None,
                #"Crazy In Love" : None,
                #"Naughty Girl" : None,
                #"Trackin'" : None,
                #"Request Line" : None,
                #"Weekends" : None,
                #"Where Is The Love" : None,
                #"Come On" : None,
                #"All Rise" : None,
                #"Hit Em Up Style" : None,
                #"Hit Em Up Style (remix)" : None,
                #"Daddy Cool" : None,
                #"Freestyler" : None,
                #"All Night Long" : None,
                #"I'm A Slave 4 U (Album)" : None,
                #"I'm A Slave 4 U (Hotmix)" : None,
                #"Bounce" : None,
                #"Missing You" : None,
                #"This Is A Test" : None,
                #"Come On Over Baby" : None,
                #"Dirrty" : None,
                #"Genie In A Bottle" : None,
                #"Lady Marmalade" : None,
                #"AM 2 PM" : None,
                #"When You Look At Me" : None,
                #"Caramel" : None,
                #"It Really Don't Matter" : None,
                #"7 Days" : None,
                #"Spanish" : None,
                #"Miss California" : None,
                #"All Good" : None,
                #"Ooh" : None,
                #"Ring, Ring (Ha Ha Hey)" : None,
                #"Dance With Me" : None,
                #"I'm A Slave 4 U (Hotmix)" : None}
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