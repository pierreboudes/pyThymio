#!/usr/bin/python
# -*- coding: utf-8 -*-
from math import atan2, pi, cos, sin, sqrt
from time import sleep
from random import gauss
import pythymio


horizon = 50
alpha = 0.1
beta = 0.01

state = {}
state["i"] = 0
state["orientation"] = 0
state["x"] = 0
state["y"] = 0
state["prox_front"] = [horizon] * 5

def position():
    return (state["x"], state["y"])

def orientation():
    return state["orientation"]

def get_prox():
    return state["prox_front"]


def todeg(angle):
    return (360.0 * angle) / (2 * pi)

#unused
def torad(angle):
    return angle / 360.0 * (2 * pi)
#unused
def cosdeg(angle):
    return cos(torad(angle))
#unused
def sindeg(angle):
    return sin(torad(angle))

def cap_direct(x, y):
    x0, y0 = position()
    angle = todeg(atan2(y - y0, x - x0))
    return angle

def cap_evitement(x, y, a = alpha):
    '''
    retourne un infléchissement angulaire de la trajectoire pour aller
    en x, y. Le paramètre a fixe la douceur d'évitement des obstacles.
    '''
    prox = get_prox()
    directions = [40, 20, 0, -20, -40]
    angle = 0
    for i in range(5):
        angle += prox[i] * directions[i]
    angle = angle / sum(prox) * 1.2
    angle = (1 - a) * angle + a * (cap_direct(x,y) - orientation())
    return angle

def reset():
    state["x"] = 100
    state["y"] = 100
    state["orientation"] = 0

def print_position_orientation():
    print "(%d, %d) %d"% (state["x"], state["y"], state["orientation"])



def distance(a, b):
    (x0, y0) = a
    (x, y) = b
    return sqrt((x - x0)**2 + (y - y0)**2)


def orienter(cap):
    if cap - orientation() > 0:
        while orientation() < cap - 10:
            yield ((-400, 400))
    else:
        while orientation() > cap + 10:
            yield ((400, -400))
    # on tourne 0.1s trop longtemps / 10° de trop... on enleve 5.

def avancer(d):
    for i in range(d):
        yield ((400, 400))

def test_cap():
    reset()
    yield "Hello I feel straight"
    for i in range(10):
        cap = cap_direct(160, 50)
        print_position_orientation()
        print cap
        # pout adoucir
        cap = 0.5 * (cap - orientation()) + orientation()
        for m in orienter(cap):
            yield m
        print_position_orientation()
        for m in avancer(20):
            yield m
        print_position_orientation()
    yield((0, 0))


def test_polygone(cote = 4):
    reset()
    yield "Hello I feel %d-squared !" % cote
    angle = 360 / cote
    for i in range(cote):
        cap = orientation() + angle
        for m in orienter(cap):
            yield m
        for m in avancer(10):
            yield m
    yield((0, 0))

def test_evitement():
    reset()
    yield "hello, I feel good !"
    for i in range(40):
        if distance(position(), (460, 100)) < 10:
            break
        angle = cap_evitement(460, 100, a = 0.1)
        cap = orientation() + angle
        for m in orienter(cap):
            yield m
        for m in avancer(4):
            yield m
        # avancer pendant 1s
    yield((0, 0))

#state["navigateur"] = test_cap()
#state["navigateur"] = test_polygone(cote = 4)
state["navigateur"] = test_evitement()
print state["navigateur"].next()


with pythymio.thymio(["motor", "prox"],[]) as Thym:
    def progression(evn, evt, data):
        if evt == "fwd.motor": #toutes les 0.01s
            state["i"] += 1
            # mettre a jour position et orientation
            left = data[0] / 500.0
            right = data[1] / 500.0
            delta = right - left
            state["orientation"] += delta * 0.6 # OK
            av = (right + left) * 0.04
            state["x"] += cosdeg(state["orientation"]) * av
            state["y"] += sindeg(state["orientation"]) * av
            if state["i"] == 10: #toutes les 0.1s
                state["i"] = 0
                try:
                    mg, md = state["navigateur"].next()
                except StopIteration:
                    Thym.stop()   # fin de la boucle evenementielle
                    mg, md = 0, 0 # on remet à zero des moteurs
                Thym.set('motor.left.target', [mg])
                Thym.set('motor.right.target', [md])
        if evt == "fwd.prox": # toutes les 0.1s
            def normalise(x):
                if x == 0:
                    return horizon # limite de perception
                else:
                    return x / 2500.0 * horizon # le max est 2500 ?
            state["prox_front"] = [normalise(data[i]) for i in range(5)]

    Thym.loop(progression)
