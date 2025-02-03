# Gravity Simulation

This is a small python script made with **pygame-ce** to simulate Newton gravity

It only supports Circles, at least as of now.

## Controls

| button             | action            |
|--------------------|-------------------|
| Space              | pause / unpause   |
| R                  | reset velocity    |
| Mouse Left         | change position   |
| Mouse Right        | change velocity   |
| Mouse Left + Right | change radius     |
| Wheel Click        | add / remove ball |
| ctrl               | snap to grid      |

## Hud

The buttons on top left indicate some extra info to draw

The slider bottom left is used for dt / simulation speed

The number top right is the amount of balls

## TODO

Seperate world and screen space

Add camera object