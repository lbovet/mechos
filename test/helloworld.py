#!/usr/bin/env python

# example helloworld.py

import pygtk
pygtk.require('2.0')
import gtk
import time
from threading import Thread

class HelloWorld:

    # This is a callback function. The data arguments are ignored
    # in this example. More on callbacks below.
    def hello(self, widget, data=None):
        print "Hello World"

    def delete_event(self, widget, event, data=None):
        # If you return FALSE in the "delete_event" signal handler,
        # GTK will emit the "destroy" signal. Returning TRUE means
        # you don't want the window to be destroyed.
        # This is useful for popping up 'are you sure you want to quit?'
        # type dialogs.
        print "delete event occurred"

        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

    def __init__(self):
    
        gtk.rc_parse('../gtkrc')
    
        # create a new window
        self.window = gtk.Window(gtk.WINDOW_POPUP)
        
        self.width = width = 240
        height = 320
        header = 24
        footer = 20
        
        self.window.set_default_size(width, height)
    
        # When the window is given the "delete_event" signal (this is given
        # by the window manager, usually by the "close" option, or on the
        # titlebar), we ask it to call the delete_event () function
        # as defined above. The data passed to the callback
        # function is NULL and is ignored in the callback function.
        self.window.connect("delete_event", self.delete_event)
    
        # Here we connect the "destroy" event to a signal handler.  
        # This event occurs when we call gtk_widget_destroy() on the window,
        # or if we return FALSE in the "delete_event" callback.
        self.window.connect("destroy", self.destroy)
        
        # Sets the border width of the window.
        self.window.set_border_width(10)
    
        # Creates a new button with the label "Hello World".
        self.button = gtk.Button("Close")
    
        self.container = gtk.Fixed()
        self.adj = gtk.Adjustment(value=0, lower=0, upper=width, step_incr=1)
        self.sliding = gtk.Layout(self.adj)        
        self.sliding.set_size_request(width, height-header-footer)
        
        self.container.set_size_request(width, height-header-footer)
        self.sliding.set_size(width*2, height-header-footer)
        self.content = gtk.Button("yop")
        self.content.set_size_request(width, height-header-footer)
        self.sliding.put(self.content, 0, 0)
        self.content.show()
        
        self.content.connect("clicked", self.move, None)

        
        self.container.put(self.sliding, 0, header)
        self.container.show()
    
        # When the button receives the "clicked" signal, it will call the
        # function hello() passing it None as its argument.  The hello()
        # function is defined above.
        self.button.connect("clicked", self.hello, None)
    
        # This will cause the window to be destroyed by calling
        # gtk_widget_destroy(window) when "clicked".  Again, the destroy
        # signal could come from here, or the window manager.
        self.button.connect_object("clicked", gtk.Widget.destroy, self.window)
    
        self.container.put(self.button, 0, 0)
        self.sliding.show()
    
        # This packs the button into the window (a GTK container).
        self.window.add(self.container)
        self.container.show()
        
        # The final step is to display this newly created widget.
        self.button.show()
    
        # and the window
        self.window.show()

    def move(self, widget, data=None):
        for i in range(0, self.width, 10):
            self.adj.set_value(i)
        for i in reversed(range(0, self.width, 10)):
            self.adj.set_value(i)
        
    def moveit(self):
        pass

    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
    hello = HelloWorld()
    hello.main()
