# Gravity Simulation

This is a small python script made with `pygame-ce` and `numpy` to simulate Newton gravity.
This originally started as a random project i just wanted to do. Now it hosts ~1000 lines of messy undocumented code that only 3am me is able to decipher. But it has turned out kind of nice. No bugs i think and i really love the ui/ux. I mean i hope its as intuitive as i think it is

# Controls

| button             | action                         |
|--------------------|--------------------------------|
| Space              | pause / unpause                |
| R                  | reset simulation / velocity    |
| H                  | toggle overlay                 |
| F11                | toggle fullscreen              |
| Esc                | Exit                           |
| Mouse Left         | change position                |
| Mouse Right        | change velocity                |
| Mouse Left + Right | change radius                  |
| Wheel              | change camera zoom / grid size |
| Wheel Click        | add / remove ball              |
| ctrl               | snap to grid                   |

# Usage

If you are on **Windows** the fastest way is to head to the releases page on the right and download the lastest **exe**

Note that the .exes are made with `autopytoexe` and will trigger Defender for seeming malicous. This is a common issue i cant solve.
https://www.reddit.com/r/learnpython/comments/e99bhe/why_does_pyinstaller_trigger_windows_defender/

If you are not on Windows or you just want to use the latest bleeding edge version, here are some steps:
- Dowload the repo `git clone https://github.com/p1geondove/grav-sim`
- Move into repo `cd grav-sim`
- create python env `python -m venv .venv`
- Optional: upgrade pip
  - Windows `.venv\Scripts\python.exe -m pip install --upgrade pip`
  - Linux `.venv/bin/python.exe -m pip install --upgrade pip`
- install requirements
  - Windows `.venv\Scripts\pip.exe install -r requirements.txt`
  - Linux `.venv/bin/pip install -r requirements.txt`
- launch
  - Windows `.venv\Scripts\python.exe main.py`
  - Linux `.venv/bin/python main.py`

I dont have a mac so i dont know what the process there is, but probably very similar

# Sample Footage

![100 Balls](./assets/100%20balls.gif)
![Euler vs. Runge-Kutta](./assets/euler%20vs%20runge-kutta.gif))

# TODO

Implement other solvers

Add more start orbits

Find and solve bugs
