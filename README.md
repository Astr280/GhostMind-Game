# GhostMind: Neon Nocturne

A polished local Pygame arcade game where four visible AI personalities navigate a living neon labyrinth. No API key, external service, or downloadable asset is required for normal play.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Run automated checks with `python -m unittest discover -s tests`.

## Controls

WASD / arrow keys move. Input is buffered so turns execute at the next valid intersection. `V` shows actual paths and explored tiles. `P` or Escape pauses; `R` restarts a game. Main menu buttons open gameplay, AI Lab, help, settings, and credits.

## AI

Red Hunter uses A*, where **f(n) = g(n) + h(n)**: `g` is the travelled cost and `h` is Manhattan-distance estimate. With unit grid costs it returns a shortest path. Blue Tracker uses BFS, which also returns a shortest route on an unweighted grid. Pink Predictor uses Greedy Best-First Search, which prioritizes only `h`, so it is fast but not guaranteed shortest. Orange Patroller switches between corner patrol and pursuit according to player proximity.

All algorithms live in `algorithms/search.py`, are independent from Pygame, expose timing and exploration metrics, and return a safe explicit no-path result. The AI Lab displays the same actual result data.

## Included features

- Three deterministic, connectivity-validated layouts, scoring, lives, power cores, respawning ghosts, progression, game over, and victory.
- Four distinct ghost personalities and explicit chase, scatter, frightened, and respawning states.
- Smooth delta-time, grid-aligned motion with queued turns; walls can never be crossed.
- Live AI overlay plus an editable AI Lab: click to edit walls, Shift-click a start, Ctrl-click a goal, then compare actual results.
- Neon Nocturne interface, original procedural characters, score particles, power bursts, hover feedback, and responsive resize-aware composition.
- Defensive local high-score/settings persistence in `ghostmind_data.json`. Missing/corrupt data falls back safely.
- Quiet procedural arcade cues cover collectibles, power cores, hunter purges, life loss, sector clear, and game-over. They are generated locally, use low gain, and respect the saved mute setting—no external audio asset is required.

## Release checklist

- [x] Local virtual environment and dependencies
- [x] Headless rendering smoke test
- [x] Search, connectivity, movement, and scoring tests
- [ ] Manual desktop playthrough: clear every sector, consume a core, catch a ghost, lose a life, pause/resume
- [ ] Optional: add original local sound files and connect them to the existing mute preference
- [ ] Optional: package with PyInstaller after a desktop QA pass

## Limitations / extension ideas

The game uses procedural art and silent graceful fallbacks rather than shipped audio assets. AI Lab executes searches immediately instead of animating each individual frontier expansion. A full desktop playthrough and PyInstaller build should be performed before public release.
