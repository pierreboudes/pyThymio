#!/usr/bin/python
# -*- coding: utf-8 -*-
import dbus
import dbus.mainloop.glib
import tempfile
import gobject

node = "thymio-II"

ThymioVariables = ["event.args", "button.backward", "button.left", "button.center", "button.forward", "button.right", "prox.horizontal", "prox.comm.rx", "prox.comm.tx", "prox.ground.ambiant", "prox.ground.reflected", "prox.ground.delta", "motor.left.target", "motor.right.target", "motor.left.speed", "motor.right.speed", "motor.left.pwm", "motor.right.pwm", "acc", "temperature", "rc5.address", "rc5.command", "mic.intensity", "mic.threshold", "timer.period"]


ThymioEvents = dict([("button.backward", []),
                ("button.left", []),
                ("button.center", []),
                ("button.forward", []),
                ("button.right", []),
                ("buttons", ["button.backward", "button.left", "button.center", "button.forward", "button.right"]),
                ("prox", ["prox.horizontal[0]", "prox.horizontal[1]", "prox.horizontal[2]", "prox.horizontal[3]", "prox.horizontal[4]", "prox.horizontal[5]", "prox.horizontal[6]", "prox.ground.ambiant[0]", "prox.ground.ambiant[1]", "prox.ground.reflected[0]", "prox.ground.reflected[1]",  "prox.ground.delta[0]", "prox.ground.delta[1]"]),
                ("prox.comm", ["prox.comm.rx"]),
                ("tap", ["acc[0]", "acc[1]", "acc[2]"]),
                ("acc", ["acc[0]", "acc[1]", "acc[2]"]),
                ("mic", ["mic.intensity"]),
                ("sound.finished", []),
                ("temperature", ["temperature"]),
                ("rc5", ["rc5.address", "rc5.command"]),
                ("motor", ["motor.left.speed", "motor.right.speed", "motor.left.pwm", "motor.right.pwm"]),
                ("timer0", []),
                ("timer1", [])])


class thymio(object):
    def __init__(self, SelectedEvents, CustomEvents):
        """ Prepare the communication and events propagation on both sides,
            Thymio and the present computer, via DBus.
        """
        # Settle a network access to Thymio through DBus
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SessionBus() # we use session bus (alternative: system bus)
        self.network = dbus.Interface(
            self.bus.get_object('ch.epfl.mobots.Aseba', '/'),
            dbus_interface='ch.epfl.mobots.AsebaNetwork')

        with tempfile.NamedTemporaryFile(suffix='.aesl', delete=False) as aesl:
            aesl.write('<!DOCTYPE aesl-source>\n<network>\n')
            #declare global events and ...
            for evt in SelectedEvents:
                aesl.write('<event size="%d" name="fwd.%s"/>\n'
                           % (len(ThymioEvents[evt]), evt))
            for (evt, code) in CustomEvents:
                aesl.write('<event size="0" name="'+ evt +'"/>\n')
            aesl.write('<node nodeId="1" name="'+node+'">\n')
            #...forward some local events as outgoing global ones
            if 'prox.comm' in SelectedEvents:
                aesl.write('call prox.comm.enable(1)')
            for evt in SelectedEvents:
                aesl.write('onevent ' + evt + "\n")
                args = ""
                if len(ThymioEvents[evt]) > 0:
                    args = "[" + ",".join(ThymioEvents[evt]) + "]"
                aesl.write ('    emit fwd.'+ evt + args + "\n")
            # add code to handle custom events
            for (evt, code) in CustomEvents:
                aesl.write('onevent ' + evt + " "+ code +"\n")
            aesl.write('</node>\n')
            aesl.write('</network>\n')

        # Load this aesl code into Thymio
        print "loading : %s into Thymio"% aesl.name
        self.network.LoadScripts(aesl.name)
        print "done"

        # Create an event filter and catch events
        self.eventfilter = self.network.CreateEventFilter()
        self.events = dbus.Interface(
            self.bus.get_object('ch.epfl.mobots.Aseba', self.eventfilter),
            dbus_interface='ch.epfl.mobots.EventFilter')

        # Listen events
        for evt in SelectedEvents:
            self.events.ListenEventName('fwd.'+evt)

        # Settle an event loop
        self.gloop = gobject.MainLoop()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.events.Free()

    def loop(self, callback):
        ''' Bind the callback and enter a loop
        '''
        self.events.connect_to_signal('Event', callback)
        self.gloop.run()

    def stop(self):
        self.gloop.quit()

    def set(self, var, vals):
        self.network.SetVariable(node, var, [dbus.Int16(x) for x in vals])
        return self

    def get(self, var):
        dbus_array = self.network.GetVariable(node, var)
        size = len(dbus_array)
        if (size == 1):
            return int(dbus_array[0])
        else:
            return [int(dbus_array[x]) for x in range(0,size)]

    def send_event(self, name, arguments = []):
        self.network.SendEventName(name, arguments)
        return self



if __name__ == '__main__':
    with thymio(["buttons"],
                [('become.yellow','call leds.top(31, 31, 0)'),
                 ('become.violet','call leds.top(31, 0, 31)'),
                 ('become.green','call leds.top(0, 31, 0)'),
                 ('become.red','call leds.top(31, 0, 0)'),
                 ('become.blank', 'call leds.top(0, 0, 0)')
                ]
    ) as Thym:

        state = dict([])
        state["duration"] = 0
        state["timeout"] = 20
        def dispatch(evt_id, evt_name, evt_args):
            if evt_name == "fwd.buttons": #received every 0.1s
                state["duration"] -= 1
                if evt_args[0] == 1: #backward
                    Thym.send_event('become.yellow')
                    state["duration"] = state["timeout"]
                if evt_args[1] == 1: #left
                    Thym.send_event('become.red')
                    state["duration"] = state["timeout"]
                if evt_args[2] == 1: #center
                    Thym.send_event('become.blank')
                    Thym.stop()
                if evt_args[3] == 1: #forward
                    Thym.send_event('become.violet')
                    state["duration"] = state["timeout"]
                if evt_args[4] == 1: #right
                    Thym.send_event('become.green')
                    state["duration"] = state["timeout"]
                if state["duration"] < 1:
                    Thym.send_event('become.blank')
            else:
                print evt_name
        Thym.loop(dispatch)
        print "state is %s" % state
        print "Sayonara"



ThymioHiddenVariables = [] #TODO
ThymioHiddenEvents = [] #TODO

def standardVariables(hidden = False):
     if hidden:
         return ThymioVariables + ThymioHiddenVariables
     else:
         return ThymioVariables

def standardEvents(hidden = False):
     if hidden:
         return dict(ThymioEvents + ThymioHiddenEvents).keys()
     else:
         return dict(ThymioEvents).keys()

def customEvents(*themes):
    """ A lexicon of simple customs events, by themes
        e.g. customEvents('color', 'circle') returns a list
        of CustomEvents one can pass to thymio.
    TODO: augment
    """
    d = dict([
        ('colors',
         [('become.yellow','call leds.top(31, 31, 0)'),
          ('become.violet','call leds.top(31, 0, 31)'),
          ('become.lightblue','call leds.top(0, 31, 31)'),
          ('become.green','call leds.top(0, 31, 0)'),
          ('become.blue','call leds.top(0, 0, 31)'),
          ('become.red','call leds.top(31, 0, 0)'),
          ('become.blank', 'call leds.top(0, 0, 0)')]
        ),
        ('circle',
         [('circle.off', 'call leds.circle(0,0,0,0,0,0,0,0)'),
          ('circle.front', 'call leds.circle(31,0,0,0,0,0,0,0)'),
          ('circle.frontright', 'call leds.circle(0,31,0,0,0,0,0,0)'),
          ('circle.right', 'call leds.circle(0,0,31,0,0,0,0,0)'),
          ('circle.backright', 'call leds.circle(0,0,0,31,0,0,0,0)'),
          ('circle.back', 'call leds.circle(0,0,0,0,31,0,0,0)'),
          ('circle.backleft', 'call leds.circle(0,0,0,0,0,31,0,0)'),
          ('circle.left', 'call leds.circle(0,0,0,0,0,0,31,0)'),
          ('circle.frontleft', 'call leds.circle(0,0,0,0,0,0,0,31)')
         ]
        ),
        ('music',
         [('chord.C3', 'call sound.freq(262, 45)'),
          ('chord.E3', 'call sound.freq(330, 45)'),
          ('chord.G3', 'call sound.freq(392, 45)'),
          ('chord.B3', 'call sound.freq(494, 45)')]
        ),
        ('sound',
         [('sound.bad', 'call sound.system(4)'),
          ('sound.good', 'call sound.system(6)')]
        )
    ])
    return {e for x in themes for e in d[x]}
