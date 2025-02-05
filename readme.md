# Gravity Simulation

This is a small python script made with `pygame-ce` to simulate Newton gravity.
Its being developed and tested in python 3.13.1 (the at the time newest release of python).
I dont know how the backwards compatibily is, but since this is a basic program, i try to use standard stuff.
I think python 3.6 should also work on this aswell.
I use pygame-ce, but the code only uses native pygame keywords, so you should also be able to use a old version of pygame

It only supports Circles, at least as of now.

# Controls

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

# Usage

If you are on **Window** the fastest way is to head to the releases page on the right and downloading the lastest **exe**

If you are not on Windows or wanna you wanna use the latest bleeding edge version here are some steps
- Dowload the repo `git pull https://github.com/p1geondove/grav-sim`
- Move into repo `cd grav-sim`
- create python env `python -m venv .venv`
- Optional: upgrade pip
  - Windows `.venv\Scripts\python.exe -m pip install --upgrade pip`
  - Linux `.venv/bin/python.exe -m pip install --upgrade pip`
- install reqirements
  - Windows `.venv\Scripts\pip.exe install -r requirements.txt`
  - Linux `.venv/bin/pip install -r requirements.txt`
- launch
  - Windows `.venv\Scripts\python.exe main.py`
  - Linux `.venv/bin/python main.py`

I dont have a mac so i dont know what the process there is, but probably very similar

# TODO

Physics update: use runge kutta order 4 integration

Add different shapes