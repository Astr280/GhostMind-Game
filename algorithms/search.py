"""Reusable grid search algorithms. Coordinates are (column, row)."""
from __future__ import annotations
from dataclasses import dataclass
from collections import deque
import heapq, time
from typing import Callable

Pos = tuple[int, int]

@dataclass
class SearchResult:
    path: list[Pos]
    explored: set[Pos]
    expanded: int
    discovered: int
    ms: float
    found: bool

def _result(start: Pos, goal: Pos, walkable: Callable[[Pos], bool], mode: str) -> SearchResult:
    began = time.perf_counter()
    if not walkable(start) or not walkable(goal):
        return SearchResult([], set(), 0, 0, (time.perf_counter()-began)*1000, False)
    if start == goal:
        return SearchResult([start], {start}, 0, 1, (time.perf_counter()-began)*1000, True)
    def neigh(p: Pos):
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            q = (p[0]+dx, p[1]+dy)
            if walkable(q): yield q
    def h(p: Pos): return abs(p[0]-goal[0]) + abs(p[1]-goal[1])
    parents: dict[Pos, Pos | None] = {start: None}; explored: set[Pos] = set(); expanded = 0
    if mode == 'bfs':
        frontier = deque([start])
        while frontier:
            current = frontier.popleft(); explored.add(current); expanded += 1
            if current == goal: break
            for nxt in neigh(current):
                if nxt not in parents: parents[nxt] = current; frontier.append(nxt)
    else:
        frontier: list[tuple[int, int, Pos]] = []; counter = 0
        heapq.heappush(frontier, (h(start), counter, start)); cost = {start: 0}
        while frontier:
            _, _, current = heapq.heappop(frontier)
            if current in explored: continue
            explored.add(current); expanded += 1
            if current == goal: break
            for nxt in neigh(current):
                new_cost = cost[current] + 1
                if mode == 'greedy':
                    if nxt in parents: continue
                    parents[nxt] = current; cost[nxt] = new_cost; counter += 1; heapq.heappush(frontier, (h(nxt), counter, nxt))
                elif new_cost < cost.get(nxt, 10**9):
                    parents[nxt] = current; cost[nxt] = new_cost; counter += 1; heapq.heappush(frontier, (new_cost+h(nxt), counter, nxt))
    found = goal in parents
    path: list[Pos] = []
    if found:
        node: Pos | None = goal
        while node is not None: path.append(node); node = parents[node]
        path.reverse()
    return SearchResult(path, explored, expanded, len(parents), (time.perf_counter()-began)*1000, found)

def astar(start: Pos, goal: Pos, walkable: Callable[[Pos], bool]) -> SearchResult: return _result(start, goal, walkable, 'astar')
def bfs(start: Pos, goal: Pos, walkable: Callable[[Pos], bool]) -> SearchResult: return _result(start, goal, walkable, 'bfs')
def greedy_best_first(start: Pos, goal: Pos, walkable: Callable[[Pos], bool]) -> SearchResult: return _result(start, goal, walkable, 'greedy')
