#!/usr/bin/python
# -*- coding: utf-8 -*-
import pythymio
import random

def randomstr(s, length):
    """ return a random string with all char in s of a given length
    """
    res = ""
    for i in range(length):
        res += s[random.randint(0, len(s) - 1)]
    return res


custom = pythymio.customEvents('colors', 'circle', 'sound', 'music')

with pythymio.thymio(["buttons"], custom) as Thym:

    state = dict([])
    state["time"] = 0
    state["difficulty"] = 3
    state["delay"] = 80
    state["seq"] = randomstr("CEGB", state["difficulty"])
    state["etape"] = "play"
    state["i"] = 0

    def play(N):
        if N == "B":
            Thym.send_event('become.yellow')
            Thym.send_event('circle.back')
            Thym.send_event('chord.B3')
        if N == "C":
            Thym.send_event('become.lightblue')
            Thym.send_event('circle.left')
            Thym.send_event('chord.C3')
        if N == "E":
            Thym.send_event('become.violet')
            Thym.send_event('circle.front')
            Thym.send_event('chord.E3')
        if N == "G":
            Thym.send_event('become.green')
            Thym.send_event('circle.right')
            Thym.send_event('chord.G3')

    def dispatch(evt_id, evt_name, evt_args):
        i = state["i"] # shorter, read-only

        # https://www.thymio.org/en:thymioapi false buttons freq is 100Hz
        if evt_name == "fwd.buttons": # every 0.01 sec
            state["time"] += 0.01
            state["delay"] -= 1

            if evt_args[1] == 1 and evt_args[4] == 1: #left-right
                Thym.send_event('become.blank')
                Thym.send_event('circle.off')
                Thym.stop()

            elif state["etape"] == "ready" and state["delay"] < 0:
                if evt_args[2] == 1:#center
                    state["etape"] = "play"
                    state["i"] = 0
                    state["seq"] = randomstr("CEGB", state["difficulty"])
                    state["delay"] = 50

            elif state["etape"] == "replay" and state["delay"] < 0:
                chord = ""
                if evt_args[0] == 1: #backward
                    chord = "B"
                if evt_args[1] == 1: #left
                    chord = "C"
                if evt_args[3] == 1: #forward
                    chord = "E"
                if evt_args[4] == 1: #right
                    chord = "G"
                if len(chord) == 1:
                    state["delay"] = 30
                    if i < len(state["seq"]) and chord == state["seq"][i]:
                        play(chord)
                        state["i"] += 1
                    else:
                        state["etape"] = "lost"
                if state["i"] == len(state["seq"]):
                    state["etape"] = "won"

            elif state["etape"] == "lost" and state["delay"] < 0:
                Thym.send_event('become.red')
                Thym.send_event('sound.bad')
                Thym.send_event('circle.off')
                print "lost, back to level 2"
                state["difficulty"] = 2
                state["etape"] = "ready"
                state["delay"] = 60

            elif state["etape"] == "won" and state["delay"] < 0:
                Thym.send_event('become.green')
                Thym.send_event('sound.good')
                Thym.send_event('circle.off')
                print 'level %d completed' % (state["difficulty"] - 1)
                state["difficulty"] += 1
                state["etape"] = "ready"
                state["delay"] = 30

            elif state["etape"] == "play" and state["delay"] < 0:
                state["delay"] = 90
                if i < len(state["seq"]):
                    play(state["seq"][i])
                    state["i"] += 1
                else:
                    Thym.send_event('become.blank')
                    Thym.send_event('circle.off')
                    state["i"] = 0
                    state["etape"] = "replay"
                    state["delay"] = 60
        else: # Wat?
            print evt_name

    # Now lets start the loopy thing
    Thym.loop(dispatch)
    print "state is %s" % state
    print "Sayonara"
