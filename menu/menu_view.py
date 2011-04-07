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
motion_threshold=5.0
motion_limit=50
click_delay=0.14
slide=[15,0.02]
speed_samples=3
scroll_steps=100
scroll_delay=20
accel=500

def te():
    gtk.gdk.threads_enter()
    
def tl():
    gtk.gdk.threads_leave()

class View(object):

    logger = logging.getLogger("menu.view")

    depth = 5
    header_line_height = 16

    level_boxes = []
    
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
    delta_x = 0
    delta_y = 0
    delta_t = 0
    auto_queue = Queue()
    sample_count = 0

    def press(self, widget, event):
        auto = self.auto
        if self.state == SCROLLING:
            self.auto_queue.put([])
        if auto:
            return True
        self.sample_count = 0
        x, y = self.slide_box.get_pointer()
        self.press_x = self.last_x = x
        self.press_y = self.last_y = y
        self.state = CLICKING
        
        time.sleep(click_delay)
        
        x, y = self.slide_box.get_pointer()
        if abs(x-self.press_x) > motion_threshold: 
            self.state = SLIDING
        elif abs(y-self.press_y) > motion_threshold:
            self.state = SCROLLING        
        else:
            self.state = CLICKED
            return
                
        self.base_scroll = widget.get_vadjustment().get_value()
        self.base_slide = self.slide_adj.get_value()
        return True  

    def release(self, widget, event):
        if self.state == SCROLLING:
            #print str(self.delta_t) + " " + str(self.delta_x / self.delta_t) + " " + str(self.delta_y / self.delta_t)
            if event.time < self.last_time + motion_limit:
                self.auto_queue.put(self.auto_scroll(widget))        
        if self.state == SLIDING:
            #print str(self.delta_t) + " " + str(self.delta_x / self.delta_t) + " " + str(self.delta_y / self.delta_t)
            self.auto_queue.put(self.auto_slide(0))
        self.state = IDLE

    def row_clicked(self, widget, event):
        if self.get_level() < self.depth-1:
            self.auto_queue.put(self.auto_slide(+1))

    def motion(self, widget, event): 
        x, y = self.slide_box.get_pointer()                                        
        if self.state == SCROLLING or self.state == SLIDING:
            self.delta_x = x - self.last_x
            self.delta_y = y - self.last_y
            self.delta_t = float(event.time - self.last_time)
            
            self.sample_count += 1
            if self.sample_count > speed_samples:
                self.sample_count = 0
                self.last_x = x
                self.last_y = y
                self.last_time = event.time        
        if self.state == SCROLLING:
            self.scroll(widget, y)        
        if self.state == SLIDING:
            self.slide(widget, x)
        return True
        
    def scroll(self, widget, y):    
        adj = widget.get_vadjustment()
        (width, height) = widget.get_size_request()
        adj.set_value( min(self.base_scroll+(self.press_y-y), adj.upper-height))
        
    def slide(self, widget, x):
        adj = self.slide_adj
        adj.set_value( min(self.base_slide+(self.press_x-x), self.base_slide))

    def auto_scroll(self, widget):
        self.auto = True
        te()
        adj = widget.get_vadjustment()
        val = adj.get_value()
        tl()
        delay = scroll_delay
        if self.delta_t == 0:
            self.delta_t = 1.0
        delta_y = (delay*self.delta_y)/self.delta_t
        if delta_y == 0:
            return
        sign = delta_y / abs(delta_y)
        delta_t = delay / 1000.0
        dt2 = delta_t * delta_t
        for i in range(scroll_steps):
            dy = delta_y - sign*dt2*accel*i  
            #print dy
            val = val - dy 
            te()            
            adj.set_value(val)
            tl()
            if abs(dy) < 2:
                break
            time.sleep(delta_t)
            yield            
        self.auto = False

    def auto_slide(self, offset):
        self.auto = True
        adj = self.slide_adj
        current = adj.get_value()
        dest = (self.get_level(current)+offset)*self.width
        sign = 1 if current < dest else -1
        
        for i in range(int(sign*current), int(sign*dest), slide[step]):
            time.sleep(slide[delay])
            te()
            adj.set_value(sign*i)
            tl()
            yield
        adj.set_value(sign*dest)
        self.auto = False

    def auto_thread(self):
        while True:            
            request = self.auto_queue.get()            
            for i in request:
                if not self.auto_queue.empty():
                    break
        
    def get_level(self, pos=self.slide_adj.get_value()):
        return round(pos/self.width)
        
    def __init__(self, parent):
        self.logger.debug('init');
        self.auto_thread = threading.Thread(target=self.auto_thread)
        self.auto_thread.start()

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
         
            item_list_store = gtk.ListStore(str)
            
            item_list = gtk.TreeView()
            item_list_column = gtk.TreeViewColumn()
            cell = gtk.CellRendererText()
            cell.set_property('height', 32)
            cell.set_property('size-points', 14)
            
            item_list_column.pack_start(cell, True)
            item_list_column.add_attribute(cell, 'text', 0)
            
            item_list.append_column(item_list_column)

            item_list.set_size_request(width, item_box_height)
            item_list.set_headers_visible(False)
            item_list.connect("button_press_event", self.press)
            item_list.connect("button_press_event", self.row_clicked)
            item_list.connect("button_release_event", self.release)
            item_list.connect("motion_notify_event", self.motion)
            item_list.show()

            event_box = gtk.EventBox()
            
            event_box.set_size_request(width, item_box_height)
            
            item_list.set_model(item_list_store)
            item_list_store.append(['hello'])
            item_list_store.append(['world'])
            item_list_store.append(['config.py'])
            item_list_store.append(['customize.py'])
            item_list_store.append(['database.py'])
            item_list_store.append(['dict.py'])
            item_list_store.append(['formula'])
            item_list_store.append(['gendoc'])
            item_list_store.append(['generic'])
            item_list_store.append(['__init__.py'])
            item_list_store.append(['log.py'])
            item_list_store.append(['maillog.py'])
            item_list_store.append(['meteo.py'])
            item_list_store.append(['setup.py'])
            item_list_store.append(['storage'])
            item_list_store.append(['storagecopy.py'])
            item_list_store.append(['test'])
            item_list_store.append(['units.py'])
            item_list_store.append(['utils.py'])
            item_list_store.append(['dict.py'])
            item_list_store.append(['formula'])
            item_list_store.append(['gendoc'])
            item_list_store.append(['generic'])
            item_list_store.append(['__init__.py'])
            item_list_store.append(['log.py'])
            item_list_store.append(['maillog.py'])
            item_list_store.append(['meteo.py'])
            item_list_store.append(['setup.py'])
            item_list_store.append(['storage'])
            item_list_store.append(['storagecopy.py'])
            item_list_store.append(['test'])
            item_list_store.append(['units.py'])
            item_list_store.append(['utils.py'])
                                    
            item_box.add(item_list)
            
            self.level_boxes.append(level_box)
            
        slide_box.show()

        #self.slide_adj.set_value(width/2)
