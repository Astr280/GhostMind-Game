# GhostMind Demonstration Guide

## Start the game

```powershell
cd "D:\GhostMind Game"
.\.venv\Scripts\python.exe main.py
```

## Five minute demonstration

1. Open **Settings** and show Easy, Medium, and Hard difficulty.
2. Start **Play**. Explain the compact HUD, 1UP token, power cores, and opening grace period.
3. Collect a power core. Show frightened ghosts, then catch one.
4. Press `V` to reveal each calculated route and current search metrics.
5. Pause with `P`, then resume.
6. Return to the menu and open **AI Lab**. Edit a wall, set a start with Shift-click, set a goal with Ctrl-click, and compare A*, BFS, and Greedy Best-First Search.

## Controls

| Action | Key |
|---|---|
| Move | WASD or Arrow Keys |
| Pause | P or Escape |
| Toggle AI diagnostics | V |
| Restart run | R |
| Mute | Settings screen |

## Pre-demo checks

Run `python -m unittest discover -s tests` inside the virtual environment. Confirm the window opens, audio is at a comfortable level, and the selected difficulty is Easy for a first demonstration.
