# GhostMind AI Powered Maze Chase Project Report

## Abstract

GhostMind is a local two-dimensional arcade maze game built with Python and Pygame. It demonstrates practical artificial intelligence through four enemy personalities that navigate the same walkable maze graph as the player. The project uses A*, Breadth-First Search, Greedy Best-First Search, a patrol state machine, and measured search metrics.

## Problem Statement

Classic maze chase games are useful for demonstrating search, but random enemy movement does not show how pathfinding decisions are made. GhostMind addresses this gap with visible, reusable algorithms and an interactive AI Lab.

## Objectives

- Create a responsive, playable maze chase game.
- Use correct local search algorithms for enemy navigation.
- Visualize genuine routes and expanded nodes on demand.
- Provide an educational comparison environment for the algorithms.
- Keep installation local and simple.

## Methodology and Implementation

The maze is a deterministic tile graph. Each walkable tile connects to its four walkable neighbors. Red Hunter uses A* with Manhattan distance. Blue Tracker uses BFS. Pink Predictor uses Greedy Best-First Search toward a validated projected player tile. Orange Patroller switches between patrol and pursuit based on Manhattan distance.

Player and ghost movement interpolate between tile centres with delta time. A queued direction is applied at the next valid intersection. Continuous-position collision checks prevent entities from crossing through one another at higher speeds. Power cores switch ghosts into a slower frightened state, while the 1UP token awards an additional life.

## Results

The current automated suite contains ten checks covering algorithms, connectivity, layout variation, movement, scoring, power mode, one-up collection, and collision response. The most recent run passed all checks.

## Conclusion and Future Scope

GhostMind provides a complete local demonstration of graph search in a playable arcade setting. Future work may add recorded sound assets, replay data, animated AI Lab frontier stepping, and a packaged executable after final desktop QA.
