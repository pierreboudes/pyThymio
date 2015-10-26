#!/usr/bin/python
# -*- coding: utf-8 -*-

import dbus
import dbus.mainloop.glib
import tempfile

thymio = "thymio-II"

# first we need the network access to Thymio through DBus
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus() # we use session bus (alternative: system bus)
network = dbus.Interface(bus.get_object('ch.epfl.mobots.Aseba', '/'), 
                         dbus_interface='ch.epfl.mobots.AsebaNetwork')

"""
Event listening

the Thymio has to run a code forwarding interesting local events.
Lets write our own aesl source file for that purpose.
"""

with tempfile.NamedTemporaryFile(suffix='.aesl', delete=False) as aesl:    
    aesl.write('<!DOCTYPE aesl-source>\n<network>\n')    
    #declare global events and ...
    aesl.write('<event size="0" name="fwd.button.backward"/>\n')
    aesl.write('<event size="0" name="become.yellow"/>\n')
    aesl.write('<event size="0" name="fwd.timer0"/>\n')
    aesl.write('<node nodeId="1" name="'+thymio+'">\n')
    #...forward some local events as outgoing global ones
    aesl.write('onevent button.backward\n    emit fwd.button.backward\n')
    aesl.write('onevent timer0\n    emit fwd.timer0\n')
    # add code to handle incoming events
    aesl.write('onevent become.yellow\n    call leds.top(31,31,0)\n')
    aesl.write('</node>\n')
    aesl.write('</network>\n')

#load the aesl code into Thymio
network.LoadScripts(aesl.name)
print "%s loaded into Thymio"% aesl.name 

#Create an event filter and catch events
eventfilter = network.CreateEventFilter()
events = dbus.Interface(
        bus.get_object('ch.epfl.mobots.Aseba', eventfilter),
        dbus_interface='ch.epfl.mobots.EventFilter')

# pushing or releasing the backward button will turn Thymio into yellow
def evt_callback(*args):
        if args[1] == "fwd.button.backward":
            print "** backward button pressed or released **"
            network.SendEventName('become.yellow', [])
        elif args[1] == "fwd.timer0":
            print 'tick'
        else:
            print [args]

network.SetVariable(thymio, "timer.period", [1000,0])
events.ListenEventName('fwd.timer0') # not required for the first event in aesl file!
events.ListenEventName('fwd.button.backward')
events.connect_to_signal('Event', evt_callback)

# Run an event loop
import gobject
loop = gobject.MainLoop()
loop.run()


