# GhostMind Test Cases and Results

| ID | Scenario | Expected result | Result |
|---|---|---|---|
| T01 | A* search in obstacle grid | Returns a shortest valid route | Pass |
| T02 | BFS search in obstacle grid | Returns a shortest valid route | Pass |
| T03 | Greedy search in obstacle grid | Returns a valid route without wall traversal | Pass |
| T04 | Unreachable target | Returns `found=False` without a crash | Pass |
| T05 | Level connectivity | Every coin, core, token, and spawn is reachable | Pass |
| T06 | Level identity | Sectors 1 to 3 have distinct layouts | Pass |
| T07 | Player movement | Position interpolates smoothly and remains walkable | Pass |
| T08 | Energy collection | A coin scores once only | Pass |
| T09 | Power core | Activates a non-zero frightened timer | Pass |
| T10 | 1UP token | Adds one life and disappears | Pass |
| T11 | Ghost catch | Continuous-distance collision starts a respawn freeze | Pass |

Automated command executed: `python -m unittest discover -s tests`.

Manual QA remains recommended for the final desktop window, especially keyboard feel, audio volume, pause/resume, and a full three-sector playthrough.
