# GhostMind System Architecture

```mermaid
flowchart TD
    Main[main.py screen manager] --> Game[game.py gameplay state]
    Main --> Lab[AI Lab]
    Main --> Audio[audio.py procedural sounds]
    Main --> Save[persistence.py JSON preferences]
    Game --> Maze[maze.py level graph]
    Game --> Entities[entities.py player and ghosts]
    Entities --> Search[algorithms/search.py]
    Search --> AStar[A star]
    Search --> BFS[Breadth First Search]
    Search --> Greedy[Greedy Best First Search]
```

The game loop separates input, movement, target selection, pathfinding, collision resolution, sound events, and rendering. Search functions do not import Pygame, so automated tests can validate routes independently from the window.
