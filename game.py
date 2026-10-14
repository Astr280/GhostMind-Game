from __future__ import annotations
import math, pygame
from config import *
from maze import Maze
from entities import Player, Ghost, DIRS

class Game:
    def __init__(self,high_score=0,difficulty='MEDIUM',show_paths=False):
        self.high=high_score; self.difficulty=difficulty; self.viz=show_paths; self.score=0; self.lives=3; self.particles=[]; self.popups=[]; self.sound_events=[]; self.reset(1,True)
    def reset(self,level=1,fresh=False):
        self.level=level; self.maze=Maze.build(level); self.player=Player(self.maze.player_spawn,speed=PLAYER_SPEED)
        specs=[('RED HUNTER',RED,'A*'),('BLUE TRACKER',CYAN,'BFS'),('PINK PREDICTOR',PINK,'GREEDY'),('ORANGE PATROLLER',ORANGE,'A*')]
        self.ghosts=[Ghost(p,name=n,color=c,algorithm=a,spawn=p) for p,(n,c,a) in zip(self.maze.ghost_spawns,specs)]
        if fresh:self.score=0;self.lives=3
        self.power=0.;self.message='GET READY';self.message_timer=3.;self.invulnerable=1.4;self.respawn_timer=0.;self.opening_timer=2.5
    def take_sounds(self): result=self.sound_events[:];self.sound_events.clear();return result
    def award(self,amount,pos,label=None):self.score+=amount;self.high=max(self.high,self.score);self.popups.append([list(pos),label or f'+{amount}',.72])
    def burst(self,pos,color,count=8):
        for i in range(count):
            a=i*math.tau/count;self.particles.append([list(pos),[math.cos(a)*2.2,math.sin(a)*2.2],color,.42])
    def update(self,dt):
        self.power=max(0,self.power-dt);self.invulnerable=max(0,self.invulnerable-dt);self.message_timer=max(0,self.message_timer-dt);self.opening_timer=max(0,self.opening_timer-dt)
        # A caught player pauses the simulation briefly instead of sliding onward.
        if self.respawn_timer>0:
            self.respawn_timer-=dt
            if self.respawn_timer<=0:
                self.player=Player(self.maze.player_spawn,speed=PLAYER_SPEED);self.invulnerable=1.15
                for g in self.ghosts:g.tile=g.spawn;g.position[:]=g.spawn;g.next_tile=None;g.path=[];g.replan_timer=0
            return None
        self.player.update(self.maze,dt);p=self.player.tile
        # Standard energy drops vanish cleanly into the player: no scatter effect.
        if p in self.maze.coins:self.maze.coins.remove(p);self.score+=COIN_SCORE;self.high=max(self.high,self.score);self.sound_events.append('coin')
        if p in self.maze.powers:
            self.maze.powers.remove(p);self.award(POWER_SCORE,p,'POWER CORE');self.power=DIFFICULTIES[self.difficulty]['power'];self.message='POWER SURGE';self.message_timer=1.5;self.burst(p,WHITE,16);self.sound_events.append('power')
        if self.maze.life_token == p:
            self.maze.life_token=None;self.lives+=1;self.award(0,p,'1UP // EXTRA LIFE');self.message='EXTRA LIFE';self.message_timer=1.8;self.burst(p,(90,255,140),14);self.sound_events.append('clear')
        cfg=DIFFICULTIES[self.difficulty]
        # Let a new player establish a route before hunters leave the pen.
        if self.opening_timer>0:
            self._update_effects(dt)
            return None
        for ghost in self.ghosts:
            ghost.update(self.player,self.maze,dt,self.power>0,cfg['ghost'],cfg['replan'])
            # Continuous collision prevents a fast ghost and player from crossing
            # through each other between tile centres.
            dx=ghost.position[0]-self.player.position[0];dy=ghost.position[1]-self.player.position[1]
            if dx*dx+dy*dy <= .42 and self.invulnerable<=0:
                if ghost.state=='FRIGHTENED':ghost.state='RESPAWNING';ghost.respawn=2.5;ghost.path=[];ghost.next_tile=None;self.award(GHOST_SCORE,p,'HUNTER PURGED');self.burst(p,ghost.color,14);self.sound_events.append('ghost')
                elif ghost.state!='RESPAWNING':
                    self.lives-=1;self.message='SIGNAL LOST';self.message_timer=1.5;self.invulnerable=1.6;self.burst(p,RED,18);self.sound_events.append('lost')
                    if self.lives<=0:self.high=max(self.high,self.score);self.sound_events.append('over');return 'gameover'
                    self.player.next_tile=None;self.respawn_timer=.75
        self._update_effects(dt)
        if not self.maze.coins:
            self.award(LEVEL_SCORE,p,'SECTOR CLEAR');self.sound_events.append('clear')
            if self.level>=3:return 'victory'
            self.reset(self.level+1);self.message='SECTOR UNLOCKED';self.message_timer=2
    def _update_effects(self,dt):
        for a in self.particles[:]:a[0][0]+=a[1][0]*dt*9;a[0][1]+=a[1][1]*dt*9;a[3]-=dt; a[3]<=0 and self.particles.remove(a)
        for a in self.popups[:]:a[0][1]-=dt*.7;a[2]-=dt;a[2]<=0 and self.popups.remove(a)
    def draw(self,surf,fonts):
        w,h=surf.get_size();surf.fill((0,0,0));tile=max(17,min(32,(h-150)//self.maze.height,(w-90)//self.maze.width));mw=self.maze.width*tile;ox=(w-mw)//2;oy=112
        def r(p):return pygame.Rect(ox+p[0]*tile,oy+p[1]*tile,tile,tile)
        def c(p):return(int(ox+(p[0]+.5)*tile),int(oy+(p[1]+.5)*tile))
        # Continuous glowing wall geometry: visual language deliberately echoes classic arcade mazes, without copied art.
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if (x,y) in self.maze.walls:
                    box=r((x,y));pygame.draw.rect(surf,(35,5,40),box,border_radius=max(4,tile//5));pygame.draw.rect(surf,PINK,box.inflate(-3,-3),2,border_radius=max(3,tile//6));pygame.draw.rect(surf,(255,110,140),box.inflate(-8,-8),1,border_radius=max(2,tile//8))
        for p in self.maze.coins:pygame.draw.circle(surf,(210,215,255),c(p),max(2,tile//12))
        pulse=1+math.sin(self.player.anim*7)*.15
        for p in self.maze.powers:pygame.draw.circle(surf,(80,80,130),c(p),int(tile*.34*pulse));pygame.draw.circle(surf,WHITE,c(p),int(tile*.19*pulse))
        if self.viz:
            for g in self.ghosts:
                if g.result:
                    for p in g.path:pygame.draw.circle(surf,g.color,c(p),max(2,tile//8))
                    pygame.draw.rect(surf,g.color,r(g.target).inflate(-5,-5),1)
        pc=c(self.player.position);rad=int(tile*.40);pygame.draw.circle(surf,(255,207,0),pc,rad);dx,dy=DIRS[self.player.direction];angle=math.atan2(dy,dx);aperture=.42+max(0,math.sin(self.player.anim*10))*.12;pygame.draw.polygon(surf,(0,0,0),[pc,(pc[0]+math.cos(angle-aperture)*rad,pc[1]+math.sin(angle-aperture)*rad),(pc[0]+math.cos(angle+aperture)*rad,pc[1]+math.sin(angle+aperture)*rad)])
        for g in self.ghosts:
            gc=c(g.position);rad=int(tile*.37)
            if g.state=='RESPAWNING':pygame.draw.circle(surf,WHITE,(gc[0]-rad//3,gc[1]),max(2,rad//4));pygame.draw.circle(surf,WHITE,(gc[0]+rad//3,gc[1]),max(2,rad//4));continue
            col=FRIGHT if g.state=='FRIGHTENED' else g.color;pygame.draw.circle(surf,col,(gc[0],gc[1]-rad//4),rad);pygame.draw.rect(surf,col,(gc[0]-rad,gc[1]-rad//4,rad*2,rad+4));pygame.draw.polygon(surf,col,[(gc[0]-rad,gc[1]+rad),(gc[0]-rad//2,gc[1]+rad//2),(gc[0],gc[1]+rad),(gc[0]+rad//2,gc[1]+rad//2),(gc[0]+rad,gc[1]+rad)])
            for ex in(-rad//3,rad//3):pygame.draw.circle(surf,WHITE,(gc[0]+ex,gc[1]-rad//5),max(2,rad//3));pygame.draw.circle(surf,(20,30,90),(gc[0]+ex,gc[1]-rad//5),max(1,rad//7))
        if self.maze.life_token:
            tc=c(self.maze.life_token); pygame.draw.circle(surf,(28,110,70),tc,int(tile*.34));pygame.draw.circle(surf,(90,255,140),tc,int(tile*.29),1); token=fonts['tiny'].render('1↑',True,WHITE);surf.blit(token,(tc[0]-token.get_width()//2,tc[1]-token.get_height()//2))
        for a in self.particles:pygame.draw.circle(surf,a[2],c(a[0]),max(1,int(tile*.1*a[3]/.42)))
        for a in self.popups:surf.blit(fonts['small'].render(a[1],True,GOLD),c(a[0]))
        self._hud(surf,fonts,w,oy+tile*self.maze.height)
    def _hud(self,surf,fonts,w,bottom):
        def centered(value,y,font,color):
            image=fonts[font].render(value,True,color);surf.blit(image,(w//2-image.get_width()//2,y))
        left=fonts['label'].render(f'1UP  {self.score:06}',True,WHITE);right=fonts['label'].render(f'HIGH SCORE  {self.high:06}',True,WHITE);surf.blit(left,(max(28,w//2-420),30));surf.blit(right,(min(w-280,w//2+80),30));centered(f'SECTOR {self.level}   ◈ {self.lives}',61,'small',GOLD)
        if self.respawn_timer>0:centered('SIGNAL LOST // REBOOTING',bottom+18,'small',RED)
        elif self.opening_timer>0:centered(f'GET READY  {self.opening_timer:0.1f}',bottom+18,'small',YELLOW)
        elif self.power>0:centered(f'POWER SURGE  {self.power:0.1f}s',bottom+18,'small',YELLOW)
        elif self.message_timer>0:centered(self.message,bottom+18,'small',YELLOW)
        if self.viz:
            info='   '.join(f'{g.algorithm}:{g.result.expanded if g.result else 0}n/{len(g.path)}p' for g in self.ghosts);centered(info,bottom+43,'small',MUTED)
        else:centered('V: AI DIAGNOSTICS    P: PAUSE    R: RESTART',bottom+43,'small',MUTED)
