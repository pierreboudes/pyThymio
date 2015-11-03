#!/usr/bin/python
# -*- coding: utf-8 -*-
import pythymio
import random

from gardenworld import *
init('info2_1')

with pythymio.thymio(["acc"],[]) as Thym:

    state = dict([])
    state["time"] = 0
    state["delay"] = 10

    def dispatch(evtid, evt_name, evt_args):
        # https://www.thymio.org/en:thymioapi prox freq is 16Hz
        if evt_name == "fwd.acc": # every 0.0625 sec
            state["time"] += 0.0625
            state["delay"] -= 1
            if state["delay"] < 0:
                if  7 < evt_args[1] < 14:
                    if evt_args[0] > 10:
                        state["delay"] = 20
                        tg()
                    elif evt_args[0] < -10:
                        state["delay"] = 20
                        td()
                elif evt_args[1] > 20 and abs(evt_args[0]) < 8:
                    state["delay"] = 10
                    av()
                elif  evt_args[1] < 5:
                    if evt_args[0] > 10:
                        state["delay"] = 20
                        dp()
                    elif evt_args[0] < -10:
                        state["delay"] = 20
                        ra()

        else: # Wat?
            print evt_name

    # Now lets start the loopy thing
    Thym.loop(dispatch)
    print "state is %s" % state
    print "Sayonara"
