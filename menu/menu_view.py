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
import gtk
from Queue import Queue
import threading
import time
import gobject

# states
IDLE = 0
CLICKING = 1
SCROLLING = 2
SLIDING = 3
CLICKED = 4

# array index
step=0
delay=1

# tuning
motion_threshold_x=15.0
motion_threshold_y=5.0
motion_limit=100
click_steps=15
click_delay=10
slide=[42,0.012]
slide_ratio=1.5
speed_samples=1
scroll_steps=1000
scroll_delay=45
motion_delay=20
accel=120
ratio=1
max_speed=2

class View(object):

    logger = logging.getLogger("menu.view")

    depth = 5
    header_line_height = 0

    item_lists = []
    
    state = IDLE 
    auto = False

    width = 0
    press_x = 0
    press_y = 0
    base_scroll = 0
    base_slide = 0
    last_x = 0
    last_y = 0
    last_time = 0
    last_move_time = 0
    speed_x = 0
    speed_y = 0
    auto_queue = Queue()
    node_provider = None
    current_path = []

    def press(self, widget, event):
        self.clear_selection()   
        interrupt = False
        if self.auto:
            interrupt = True
            self.auto = False
        self.sample_count = 0
        x, y = self.slide_box.get_pointer()
        self.press_x = self.last_x = x
        self.press_y = self.last_y = y
        self.state = CLICKING
        
        for i in range(click_steps):
            time.sleep(click_delay/1000.0)
            x, y = self.slide_box.get_pointer()
            if abs(x-self.press_x) > motion_threshold_x: 
                self.state = SLIDING
                break
            elif abs(y-self.press_y) > motion_threshold_y:
                self.state = SCROLLING        
                break
                
        if self.state == CLICKING:
            self.state = CLICKED
            if interrupt:            
                return True
            else:
                path = widget.get_path_at_pos(int(event.x), int(event.y))
                if path:
                    widget.set_cursor(path[0])                
                return
                
        self.base_scroll = widget.get_vadjustment().get_value()
        self.base_slide = self.slide_adj.get_value()
        
        self.motion(widget)
        return True  

    def release(self, widget, event):
        if self.state == SCROLLING:
            if event.time < self.last_time + motion_limit:
                self.auto_scroll(widget) 
        if self.state == SLIDING:
            self.auto_slide(widget, 0)
            self.update_level()
        self.state = IDLE

    def row_clicked(self, widget, event):
        if not widget.get_path_at_pos(int(event.x), int(event.y)):
            return
        level = self.get_level() 
        if level < self.depth-1:
            if widget.get_cursor():                
                self.current_path.append(widget.get_cursor()[0][0])
                list = self.node_provider(self.current_path)
                if list:
                    item_list_store = gtk.ListStore(str)
                    for i in list:
                        item_list_store.append([i])
                    self.item_lists[level+1].set_model(item_list_store)            
                    self.auto_queue.put(self.auto_slide(widget, +1))
            self.update_level()

    def motion(self, widget):
        while self.state != IDLE:
            while gtk.events_pending():
                gtk.main_iteration(False)

            t = time.time()*1000
            if self.auto:
                self.speed_y = 0
                return 
            x, y = self.slide_box.get_pointer()                                        
            if self.state == SCROLLING or self.state == SLIDING:
                delta_x = x - self.last_x
                delta_y = y - self.last_y
                delta_t = float(t - self.last_time)
                
                if delta_t != 0 and delta_y != 0:
                    self.speed_x = delta_x / delta_t
                    speed_y = delta_y / delta_t
                    self.speed_y = sign(speed_y)*min(abs(speed_y), max_speed)
                
                self.last_x = x
                self.last_y = y
                self.last_time = t        
            if self.state == SCROLLING:
                if t > self.last_move_time + 100:
                    self.scroll(widget, y)        
                    self.last_move_time = t
            if self.state == SLIDING:
                self.slide(widget, x)
            time.sleep(motion_delay/1000.0)
        
    def scroll(self, widget, y):    
        adj = widget.get_vadjustment()
        (width, height) = widget.get_size_request()
        adj.set_value( min(self.base_scroll+(self.press_y-y), adj.upper-height))
        
    def slide(self, widget, x):
        adj = self.slide_adj
        adj.set_value( min(self.base_slide-min(x*slide_ratio-self.press_x, self.width), self.base_slide))

    def auto_scroll(self, widget):
        self.auto = True
        (width, height) = widget.get_size_request()
        adj = widget.get_vadjustment()
        val = adj.get_value()
        delay = scroll_delay

        if self.speed_y == 0:
            self.auto=False
            return

        delta_y = delay*self.speed_y

        sign = delta_y / abs(delta_y)
        delta_t = delay / 1000.0
        dt2 = delta_t * delta_t
        for i in range(scroll_steps):
            dy = delta_y - sign*dt2*accel*i  
            val = val - dy          
            if val < adj.lower:
                adj.set_value(adj.lower)
                break
            if val > adj.upper-height:
                adj.set_value(adj.upper-height)
                break
            adj.set_value(val)
            if dy*sign < 2:
                break
            time.sleep(delta_t)
            while gtk.events_pending():
                gtk.main_iteration(False)
            if not self.auto:
                break

        self.auto = False

    def auto_slide(self, widget, offset):    
        self.auto = True
        adj = self.slide_adj
        current = adj.get_value()
        dest = (self.get_level(current)+offset)*self.width
        if current < dest:
            sign = 1 
        else:
            sign = -1
        
        for i in range(int(sign*current), int(sign*dest), slide[step]):
            time.sleep(slide[delay])
            adj.set_value(sign*i)
            while gtk.events_pending():
                gtk.main_iteration(False)
        adj.set_value(dest)
        self.auto = False
        self.clear_selection()   

    def auto_thread(self):         
        request = self.auto_queue.get_nowait()            
        if request:
            for i in request:
                if not self.auto_queue.empty():
                    break
        
    def get_level(self, pos=None):
        if pos == None:
            pos = self.slide_adj.get_value()
        return int(round(pos/self.width))
        
    def update_level(self):
        self.current_path = self.current_path[:self.get_level()]
        
    def clear_selection(self):
        for i in self.item_lists:
            i.get_selection().unselect_all()
        
    def __init__(self, parent):
        self.logger.debug('init');

        (width, height) = parent.get_size_request()
        self.width = width
    
        self.slide_adj = gtk.Adjustment(value=0, lower=0, upper=width*self.depth, step_incr=1)    
        slide_box = gtk.Layout(self.slide_adj)        
        self.slide_box = slide_box
        slide_box.set_size_request(width, height)
        slide_box.set_size(width*self.depth, height)
        
        parent.add(slide_box)
        
        for i in range(self.depth):
            level_box = gtk.Fixed()
            level_box.set_size_request(width, height)
            slide_box.put(level_box, width*i, 0)
            level_box.show()
            
            header_box = gtk.Fixed()
            header_height = self.header_line_height*i
            header_box.set_size_request(width, header_height)
            header_box.show()
            level_box.put(header_box, 0, 0)
            
            item_box = gtk.Fixed()
            item_box_height = height - header_height
            item_box.set_size_request(width, item_box_height)
            item_box.show()
            level_box.put(item_box, 0, header_height)         
            
            item_list = gtk.TreeView()
            item_list_column = gtk.TreeViewColumn()
            cell = gtk.CellRendererText()
            cell.set_property('height', 24)
            cell.set_property('size-points', 12)
            
            item_list_column.pack_start(cell, True)
            item_list_column.add_attribute(cell, 'text', 0)
            
            item_list.append_column(item_list_column)
            item_list.set_events(gtk.gdk.BUTTON_PRESS_MASK)
            item_list.set_size_request(width, item_box_height)
            item_list.set_headers_visible(False)
            item_list.connect("button_press_event", self.press)
            item_list.connect("button_press_event", self.row_clicked)
            item_list.connect("button_release_event", self.release)
            item_list.show()

            event_box = gtk.EventBox()
            
            event_box.set_size_request(width, item_box_height)
                                    
            item_box.add(item_list)
            
            self.item_lists.append(item_list)
            
        slide_box.show()

    def set_node_provider(self, node_provider):        
        self.node_provider = node_provider
        item_list_store = gtk.ListStore(str)
        for i in node_provider():
            item_list_store.append([i])    
        item_list = self.item_lists[0]
        item_list.set_model(item_list_store)
        self.clear_selection()

def sign(val):
    if val < 0:
        return -1
    if val > 0:
        return 1
    return 0
