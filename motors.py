#!/usr/bin/python
# -*- coding: utf-8 -*-
import pythymio

with pythymio.thymio(["motor"],[]) as Thym:

    state = dict([])
    state["time"] = 0
    state["left"] = [0]
    state["right"] = [0]
    state["prog"] = dict([
        (90, (500, 500)), #50 av
        (140, (0, 0)),
        (180, (-500, 500)), #108 tg
        (288, (0, 0)),
        (350, (500, 500)), #50 av
        (400, (0,0)),
        (450, (500, -500)), #108 td
        (558, (0, 0)),
        (600, (500, 500)), #50 av
        (650, (0, 0)),
        (700, (500, -500)),#108 td
        (808, (0, 0)),
        (860, (500, 500)), #50 av
        (910, (0, 0)),
        (960, (500, -500)),#108 av
        (1068, (0, 0)),
        (1120, (500, 500)),#50 av
        (1170, (0, 0))
    ])
    state["end"] = max(state["prog"].keys()) + 10

    def dispatch(evtid, evt_name, evt_args):
        global state

        # https://www.thymio.org/en:thymioapi motor freq is 100Hz
        if evt_name == "fwd.motor": # every 0.01 sec
            state["left"] += [evt_args[0]]
            state["right"] += [evt_args[1]]
            if state["time"] in state["prog"]:
                (l,r) = state["prog"][(state["time"])]
                Thym.set('motor.left.target', [l])
                Thym.set('motor.right.target', [r])
            state["time"] += 1
            if state["time"] == state["end"]:
                Thym.stop()

        else: # Wat?
            print evt_name

    # Now lets start the loopy thing
    Thym.loop(dispatch)
    print "state is %s" % state
    print [int(x) for x in state["left"]]
    print [int(x) for x in state["right"]]
    print "Sayonara"
