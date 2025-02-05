# Gravity Simulation

This is a small python script made with **pygame-ce** to simulate Newton gravity.
Its being developed and tested in python 3.13.1 (the at the time newest release of python).
I dont know how the backwards compatibily is, but since this is a basic program, i try to use standard stuff.
I think python 3.6 should also work on this aswell.
I use pygame-ce, but the code only uses native pygame keywords, so you should also be able to use a old version of pygame

It only supports Circles, at least as of now.

## Controls

| button             | action             |
|--------------------|--------------------|
| Space              | pause / unpause    |
| R                  | reset velocity     |
| Mouse Left         | change position    |
| Mouse Right        | change velocity    |
| Mouse Left + Right | change radius      |
| Wheel              | change camera zoom |
| Wheel Click        | add / remove ball  |
| ctrl               | snap to grid       |

## TODO

Physics update: use runge kutta order 4 integration

Add different shapes