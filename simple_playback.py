#!/usr/bin/python
# -*- coding: utf-8 -*-
import pythymio as pt


with pt.thymio(["buttons"], pt.customEvents('circle')) as Thym:

    state = {}
    state["delay"] = 100
    state["seq"] = "LRLRUUDD" # ← → ← → ↑ ↑ ↓ ↓
    state["i"] = 0
    state["n"] =  len(state["seq"])
    state["etape"] = "stop"

    """ etape, etape * i

       |
       V
      stop -----> read 0 -....- read n ---\
       ^                                  |
       |                                  |
       \__________________________________/

    """
    def play(s):
        if s == "L":
            Thym.send_event('circle.left')
        if s == "R":
            Thym.send_event('circle.right')
        if s == "U":
            Thym.send_event('circle.front')
        if s == "D":
            Thym.send_event('circle.back')


    def progression(evt_id, evt_name, evt_args):
        i = state["i"]
        seq = state["seq"]
        if evt_name == "fwd.buttons": #100 Hz
            state["delay"] -= 1
            if state["delay"] <= 1:
                if state["etape"] == "stop" and evt_args[2] == 1:
                    state["etape"] = "read"
                    state["i"] = 0
                    state["delay"] = 100
                elif state["etape"] == "pause":
                    print "pause"
                    state["delay"] = 60
                    state["etape"] = "read"
                    Thym.send_event('circle.off')
                elif state["etape"] == "read" and  i < state["n"]:
                    print seq[i]
                    play(seq[i])
                    state["i"] += 1
                    state["etape"] = "pause"
                    state["delay"] = 100
                elif state["etape"] == "read" and  i == state["n"]:
                    state["etape"] = "stop";

        else: # Wat?
            print evt_name

    # Now lets start the loopy thing
    Thym.loop(progression)
    print "state is %s" % state
    print "Sayonara"
