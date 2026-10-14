"""Grid-aligned, delta-time movement and personality-specific ghost control."""
from __future__ import annotations
from dataclasses import dataclass, field
from algorithms import astar, bfs, greedy_best_first, SearchResult

Pos = tuple[int, int]
DIRS = {'UP': (0,-1), 'DOWN': (0,1), 'LEFT': (-1,0), 'RIGHT': (1,0)}

@dataclass
class Mover:
    tile: Pos
    direction: str = 'LEFT'
    queued: str = 'LEFT'
    speed: float = 6.0
    position: list[float] = field(default_factory=list)
    next_tile: Pos | None = None
    anim: float = 0.0
    def __post_init__(self):
        if not self.position: self.position = [float(self.tile[0]), float(self.tile[1])]
    def _can_enter(self, maze, direction: str) -> Pos | None:
        dx,dy = DIRS[direction]; candidate=(self.tile[0]+dx,self.tile[1]+dy)
        return candidate if maze.walkable(candidate) else None
    def _start(self, maze, direction: str) -> bool:
        candidate=self._can_enter(maze,direction)
        if candidate is None: return False
        self.direction,self.next_tile=direction,candidate; return True
    def _move(self, dt: float) -> bool:
        self.anim += dt
        if self.next_tile is None: return True
        tx,ty=self.next_tile; dx,dy=tx-self.position[0],ty-self.position[1]; distance=(dx*dx+dy*dy)**.5; step=self.speed*dt
        if distance <= step:
            self.position[:]=[float(tx),float(ty)]; self.tile=self.next_tile; self.next_tile=None; return True
        self.position[0]+=dx/distance*step; self.position[1]+=dy/distance*step; return False

class Player(Mover):
    def update(self, maze, dt: float) -> None:
        if not self._move(dt): return
        if self.queued and self._start(maze,self.queued): return
        self._start(maze,self.direction)

@dataclass
class Ghost(Mover):
    name: str=''; color: tuple=(255,0,0); algorithm: str='A*'; state: str='CHASE'; spawn: Pos=(0,0)
    path: list[Pos]=field(default_factory=list); result: SearchResult|None=None; target: Pos=(0,0)
    replans: int=0; replan_timer: float=0.; respawn: float=0.; prior_state: str='CHASE'
    def choose_target(self, player: Player, maze) -> Pos:
        if self.name=='PINK PREDICTOR':
            dx,dy=DIRS[player.direction]; wanted=(player.tile[0]+dx*4,player.tile[1]+dy*4)
            if maze.walkable(wanted): return wanted
            return min(maze.walkable_tiles,key=lambda p:abs(p[0]-wanted[0])+abs(p[1]-wanted[1]))
        if self.name=='ORANGE PATROLLER':
            close=abs(self.tile[0]-player.tile[0])+abs(self.tile[1]-player.tile[1])<=7
            self.state='CHASE' if close else 'SCATTER'
            if close: return player.tile
            waypoints=[p for p in [(1,1),(maze.width-2,1),(maze.width-2,maze.height-2),(1,maze.height-2)] if maze.walkable(p)]
            return waypoints[self.replans%len(waypoints)]
        self.state='CHASE'; return player.tile
    def plan(self,player,maze) -> None:
        self.target=self.choose_target(player,maze); fn={'A*':astar,'BFS':bfs,'GREEDY':greedy_best_first}[self.algorithm]
        self.result=fn(self.tile,self.target,maze.walkable); self.path=self.result.path[1:] if self.result.found else []; self.replans+=1
    def update(self,player,maze,dt,powered,base_speed,interval) -> None:
        if self.state=='RESPAWNING':
            self.respawn-=dt
            if self.respawn<=0: self.state='CHASE'; self.tile=self.spawn; self.position[:]=self.spawn; self.next_tile=None
            return
        if powered and self.state!='FRIGHTENED': self.prior_state=self.state; self.state='FRIGHTENED'; self.path=[]
        elif not powered and self.state=='FRIGHTENED': self.state=self.prior_state; self.path=[]
        self.replan_timer-=dt
        if not self._move(dt): return
        if self.state=='FRIGHTENED':
            options=[p for d in DIRS for p in [self._can_enter(maze,d)] if p is not None]
            self.path=[max(options,key=lambda p:abs(p[0]-player.tile[0])+abs(p[1]-player.tile[1]))] if options else []
        elif self.replan_timer<=0 or not self.path or self.target!=self.choose_target(player,maze):
            self.plan(player,maze); self.replan_timer=interval
        if self.path:
            nxt=self.path.pop(0); delta=(nxt[0]-self.tile[0],nxt[1]-self.tile[1])
            for name,vector in DIRS.items():
                if vector==delta: self._start(maze,name); break
        self.speed=base_speed*(.55 if self.state=='FRIGHTENED' else 1)
