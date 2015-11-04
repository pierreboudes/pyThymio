#!/usr/bin/python
# -*- coding: utf-8 -*-
import pythymio as pt

GREATEST_SUFFIX_MATCH = True

def prefix(s, t):
    return len(s) <= len(t) and s == t[:len(s)]

with pt.thymio(["buttons"], pt.customEvents('circle')) as Thym:

    state = {}
    state["delay"] = 100
    state["seq"] = "LRLRUUDD" # ← → ← → ↑ ↑ ↓ ↓
    state["i"] = 0
    state["n"] =  len(state["seq"])
    state["etape"] = "read"
    state["readseq"] = " "

    def button2str(t):
        if t[0] == 1:
            return "D"
        if t[1] == 1:
            return "L"
        if t[3] == 1:
            return "U"
        if t[4] == 1:
            return "R"
        return "?"

    def play(s):
        if s == "L":
            Thym.send_event('circle.left')
        elif s == "R":
            Thym.send_event('circle.right')
        elif s == "U":
            Thym.send_event('circle.front')
        elif s == "D":
            Thym.send_event('circle.back')
        else:
            Thym.send_event('circle.off')

    def progression(evt_id, evt_name, evt_args):
        i = state["i"]
        seq = state["seq"]
        if evt_name == "fwd.buttons": #100 Hz
            state["delay"] -= 1
            if state["delay"] <= 1:
                if state["etape"] == "read" and  i < state["n"]:
                    b = button2str(evt_args)
                    if b != "?":
                        state["readseq"] += b
                        play(b)
                        print b
                        if GREATEST_SUFFIX_MATCH:
                            rs = state["readseq"]
                            ne = len(rs)
                            j = max([k for k in range(ne) if prefix(rs[ne - k:], seq)]+[0])
                            if j <= i:
                                Thym.send_event('sound.bad')
                            i = j
                        else:
                            if b == seq[i]: # ok
                                state["i"] += 1
                            else:
                                state["i"] = 0
                                Thym.send_event('sound.bad')
                        state["delay"] = 50
                if state["etape"] == "read" and  i == state["n"]:
                    print "Bravo !"
                    #Thym.send_event('sound.good')
                    Thym.stop()

        else: # Wat?
            print evt_name

    # Now lets start the loopy thing
    Thym.loop(progression)
    print state
    print "Sayonara"
