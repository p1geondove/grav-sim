# Gravity Simulation

This is a small python script made with `pygame-ce` to simulate Newton gravity.
This originally started as a random project i just wanted to do. After i felt like i had reached a point i made a small video and uploaded it to the pygame subreddit. It got a bit of traction so uploaded it here on and developed it further and learn about git. Now it hosts 500+ lines of messy undocumented code that only 3am me is able to decipher. But it has turned out kind of nice. No bugs i think and i really love the ui/ux

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

If you are not on Windows or you just want to use the latest bleeding edge version here are some steps
- Dowload the repo `git clone https://github.com/p1geondove/grav-sim`
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

Add boundary back, rect and circle. Make them be able to wrap or bounce the balls

Right click drag makes a selection box

Keypress for complete reset

Performance issues when scrolling in too far. Maybe add max zoom constraint

Add slider [1 - 10] for amount of update steps per draw cycle