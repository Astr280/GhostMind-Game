"""Hand-crafted, connected arcade layouts. # wall, . energy, o core, P player, 1-4 ghosts."""
from __future__ import annotations
from dataclasses import dataclass
from algorithms import bfs

BASE = [
'#####################',
'#o.................o#',
'#.###.#####.#####.###',
'#...................#',
'#.###.#.###.###.#.###',
'#.....#.....#.....#.#',
'#####.###.###.###.#.#',
'#...................#',
'#.###.##.....##.###.#',
'#...#.#.1234.###....#',
'#.###.#.#####.#.###.#',
'#...................#',
'#.###.###...###.###.#',
'#.....#.......#.....#',
'#.###.#.#####.#.###.#',
'#...#...........#...#',
'#.#####.#####.#####.#',
'#o........P........o#',
'#####################']

# These are intentionally substantial route changes, not only speed changes.
# Each tuple opens an existing wall in the fully connected base maze, which
# keeps validation deterministic while giving each sector its own silhouette.
LEVEL_OPENINGS = {
    2: ((3,2),(8,2),(12,2),(17,2),(3,4),(9,4),(15,4),(3,6),(7,6),(11,6),(15,6),(3,8),(8,8),(12,8),(17,8),(3,12),(7,12),(13,12),(17,12),(3,14),(8,14),(12,14),(17,14)),
    3: ((2,2),(4,2),(10,2),(16,2),(18,2),(6,4),(10,4),(14,4),(5,6),(9,6),(13,6),(17,6),(5,10),(9,10),(13,10),(17,10),(5,12),(9,12),(11,12),(15,12),(5,14),(9,14),(13,14),(15,14),(6,16),(10,16),(14,16)),
}

@dataclass
class Maze:
    rows:list[str]; walls:set[tuple[int,int]]; coins:set[tuple[int,int]]; powers:set[tuple[int,int]]
    player_spawn:tuple[int,int]; ghost_spawns:list[tuple[int,int]]; width:int; height:int; walkable_tiles:set[tuple[int,int]]; life_token:tuple[int,int]|None
    @classmethod
    def build(cls,level:int)->'Maze':
        sector=(level-1)%3+1
        rows=[list(row) for row in BASE]
        for x,y in LEVEL_OPENINGS.get(sector,()):
            if rows[y][x]=='#': rows[y][x]='.'
        rows=[''.join(row) for row in rows]
        if not rows or len({len(r) for r in rows})!=1:raise ValueError('maze rows must have equal width')
        walls=set(); coins=set(); powers=set(); player=(1,1); ghosts=[]
        for y,row in enumerate(rows):
            for x,char in enumerate(row):
                if char=='#':walls.add((x,y))
                elif char=='.':coins.add((x,y))
                elif char=='o':powers.add((x,y))
                elif char=='P':player=(x,y)
                elif char in '1234':ghosts.append((x,y))
        walkable={(x,y) for y,row in enumerate(rows) for x,_ in enumerate(row) if (x,y) not in walls}
        # One approachable bonus per sector; it is never placed in the ghost pen.
        token_options={1:(10,11),2:(10,7),3:(10,15)}
        life_token=token_options[sector]
        if life_token not in walkable: raise ValueError('life token must be walkable')
        maze=cls(rows,walls,coins,powers,player,ghosts,len(rows[0]),len(rows),walkable,life_token)
        if not maze.valid():raise ValueError('maze has unreachable game targets')
        return maze
    def walkable(self,p):return 0<=p[0]<self.width and 0<=p[1]<self.height and p not in self.walls
    def valid(self):
        return len(self.ghost_spawns)==4 and self.walkable(self.player_spawn) and all(bfs(self.player_spawn,p,self.walkable).found for p in self.coins|self.powers|set(self.ghost_spawns))
