"""GhostMind application and intentionally lightweight screen manager."""
import sys, math, pygame
from pathlib import Path
from config import *
from game import Game
from algorithms import astar,bfs,greedy_best_first
from persistence import load_preferences,save_preferences
from audio import AudioBus

pygame.init(); screen=pygame.display.set_mode((WIDTH,HEIGHT),pygame.RESIZABLE); pygame.display.set_caption('GhostMind: Neon Nocturne'); clock=pygame.time.Clock()
fonts={'tiny':pygame.font.SysFont('consolas',12,True),'small':pygame.font.SysFont('consolas',16),'label':pygame.font.SysFont('consolas',20,True),'heading':pygame.font.SysFont('consolas',25,True),'title':pygame.font.SysFont('consolas',58,True)}
def load_logo():
    """Load the supplied branding; fall back to the text mark if unavailable."""
    try:
        image=pygame.image.load(Path(__file__).with_name('assets')/'ghostmind_logo.png').convert()
        # The supplied PNG includes an opaque black canvas; crop its generous
        # outer margin before using black as a transparent menu color key.
        crop=pygame.Rect(90,220,1360,570).clip(image.get_rect())
        image=image.subsurface(crop).copy(); image.set_colorkey((0,0,0))
        return image
    except (pygame.error,OSError): return None
logo=load_logo()
prefs=load_preferences(); state='MENU'; game=None; buttons=[]; lab_result=None; lab_algo='A*'; lab_walls={(4,y) for y in range(1,9) if y!=5}|{(x,6) for x in range(4,12) if x!=8}; lab_start=(1,1); lab_goal=(14,9); elapsed=0.
audio=AudioBus(prefs['muted'])

def text(value,pos,font='small',color=WHITE):screen.blit(fonts[font].render(value,True,color),pos)
def panel(rect,fill=SURFACE):pygame.draw.rect(screen,fill,rect,border_radius=16); pygame.draw.rect(screen,SURFACE_2,rect,2,border_radius=16)
def button(label,rect,enabled=True):
    hover=rect.collidepoint(pygame.mouse.get_pos()); col=CYAN if hover and enabled else SURFACE_2; fill=(23,48,82) if hover and enabled else SURFACE
    pygame.draw.rect(screen,fill,rect,border_radius=11); pygame.draw.rect(screen,col,rect,2,border_radius=11); rendered=fonts['label'].render(label,True,WHITE if enabled else MUTED); screen.blit(rendered,(rect.centerx-rendered.get_width()//2,rect.centery-rendered.get_height()//2)); buttons.append((label,rect,enabled))
def backdrop():
    screen.fill(NAVY); w,h=screen.get_size()
    for x in range(0,w,48):pygame.draw.line(screen,(8,21,46),(x,0),(x,h),1)
    for y in range(0,h,48):pygame.draw.line(screen,(8,21,46),(0,y),(w,y),1)
    for i in range(18):
        x=(i*97+elapsed*35)%(w+80)-40; y=(i*149+math.sin(elapsed+i)*34)%(h+80)-40; pygame.draw.circle(screen,CYAN,(int(x),int(y)),2)
def title():
    w,_=screen.get_size()
    if logo:
        max_w,min_h=min(640,w-120),155; scale=min(max_w/logo.get_width(),min_h/logo.get_height()); size=(int(logo.get_width()*scale),int(logo.get_height()*scale)); image=pygame.transform.smoothscale(logo,size);screen.blit(image,(w//2-size[0]//2,20))
    else:
        rendered=fonts['title'].render('GHOSTMIND',True,YELLOW); screen.blit(rendered,(w//2-rendered.get_width()//2,75)); sub=fonts['label'].render('NEON NOCTURNE  //  AI-POWERED MAZE CHASE',True,CYAN); screen.blit(sub,(w//2-sub.get_width()//2,145))
def menu():
    backdrop(); title(); w,_=screen.get_size(); panel(pygame.Rect(w//2-230,205,460,490))
    for label,y in [('PLAY',240),('AI LAB',307),('HOW TO PLAY',374),('SETTINGS',441),('CREDITS',508),('QUIT',575)]:button(label,pygame.Rect(w//2-190,y,380,49))
    text('v1.1  •  LOCAL AI ARCADE', (w//2-110,660),color=MUTED)
def overlay(title_text,lines,actions):
    backdrop(); title(); w,_=screen.get_size(); box=pygame.Rect(w//2-390,205,780,500); panel(box); text(title_text,(w//2-fonts['heading'].size(title_text)[0]//2,235),'heading',YELLOW)
    y=290
    for line in lines:text(line,(w//2-340,y),color=WHITE); y+=31
    # Buttons are bottom-anchored, so long action lists never spill outside.
    y=max(y+12, box.bottom-24-len(actions)*58)
    for label in actions:button(label,pygame.Rect(w//2-160,y,320,48)); y+=60
def lab():
    backdrop(); text('AI LAB', (52,36),'title',YELLOW); text('Click a cell to toggle a wall. Shift-click sets start; Ctrl-click sets goal.',(55,105),color=MUTED)
    for label,x in [('RUN A*',55),('RUN BFS',200),('RUN GREEDY',345),('RESET GRID',510),('BACK',655)]:button(label,pygame.Rect(x,145,126,42))
    tile=39; ox,oy=55,220
    for y in range(11):
        for x in range(16):
            r=pygame.Rect(ox+x*tile,oy+y*tile,tile,tile); wall=(x,y) in lab_walls; pygame.draw.rect(screen,CYAN_DIM if wall else SURFACE,r); pygame.draw.rect(screen,BLUE if wall else SURFACE_2,r,1)
    if lab_result:
        for p in lab_result.explored:pygame.draw.circle(screen,CYAN,(ox+p[0]*tile+tile//2,oy+p[1]*tile+tile//2),4)
        for p in lab_result.path:pygame.draw.circle(screen,YELLOW,(ox+p[0]*tile+tile//2,oy+p[1]*tile+tile//2),9)
        panel(pygame.Rect(735,215,470,380)); text('SEARCH REPORT',(765,245),'heading',YELLOW)
        for i,line in enumerate([f'ALGORITHM    {lab_algo}',f'PATH FOUND   {lab_result.found}',f'EXPANDED     {lab_result.expanded}',f'DISCOVERED   {lab_result.discovered}',f'PATH LENGTH  {max(0,len(lab_result.path)-1)}',f'COMPUTE      {lab_result.ms:.3f} ms']):text(line,(765,300+i*43),'label' if i==0 else 'small',WHITE)
    pygame.draw.circle(screen,(70,255,142),(ox+lab_start[0]*tile+tile//2,oy+lab_start[1]*tile+tile//2),11); pygame.draw.circle(screen,RED,(ox+lab_goal[0]*tile+tile//2,oy+lab_goal[1]*tile+tile//2),11)
    return pygame.Rect(ox,oy,16*tile,11*tile),tile
def run_lab(name):
    global lab_result,lab_algo
    lab_algo={'RUN A*':'A*','RUN BFS':'BFS','RUN GREEDY':'GREEDY'}[name]; walk=lambda p:0<=p[0]<16 and 0<=p[1]<11 and p not in lab_walls
    lab_result={'A*':astar,'BFS':bfs,'GREEDY':greedy_best_first}[lab_algo](lab_start,lab_goal,walk)

while True:
    dt=min(clock.tick(FPS)/1000,.05); elapsed+=dt; buttons=[]; lab_grid=None
    if state=='MENU':menu()
    elif state=='PLAY':
        game.difficulty=prefs['difficulty']; outcome=game.update(dt); [audio.play(event) for event in game.take_sounds()]; game.draw(screen,fonts)
        if outcome:state=outcome.upper()
    elif state=='LAB':lab_grid=lab()
    elif state=='HELP':overlay('HOW TO PLAY',['Navigate the living labyrinth and collect every gold signal.','Power cores make the hunters frightened: collide to send them home.','RED uses A*, BLUE uses BFS, PINK predicts ahead, AMBER patrols.','WASD / arrows move.  V diagnostics.  P / Esc pause.  R restart.'],['BACK'])
    elif state=='SETTINGS':overlay('SETTINGS',[f'Difficulty: {prefs["difficulty"]}',f'Diagnostics default: {"ON" if prefs["show_paths"] else "OFF"}',f'Audio muted: {"YES" if prefs["muted"] else "NO"}','Settings are saved locally in ghostmind_data.json.'],['CHANGE DIFFICULTY','TOGGLE DIAGNOSTICS','TOGGLE MUTE','BACK'])
    elif state=='CREDITS':overlay('CREDITS',['DESIGN + CODE: GhostMind project','ART: original procedural Pygame geometry','AI: native A*, BFS, Greedy Best-First Search','AUDIO: optional; game operates without external assets.'],['BACK'])
    elif state=='PAUSE':overlay('PAUSED',['The simulation is paused. Your score and maze state are preserved.'],['RESUME','MAIN MENU'])
    elif state in ('GAMEOVER','VICTORY'):overlay('MAZE COMPLETE' if state=='VICTORY' else 'SIGNAL LOST',[f'Final score: {game.score:06}',f'Best score: {game.high:06}',f'Sector reached: {game.level}','Press Restart for a fresh run.'],['RESTART','MAIN MENU'])
    for e in pygame.event.get():
        if e.type==pygame.QUIT:save_preferences({**prefs,'high_score':game.high if game else prefs['high_score']}); pygame.quit(); sys.exit()
        if e.type==pygame.KEYDOWN:
            if state=='PLAY':
                moves={pygame.K_w:'UP',pygame.K_UP:'UP',pygame.K_s:'DOWN',pygame.K_DOWN:'DOWN',pygame.K_a:'LEFT',pygame.K_LEFT:'LEFT',pygame.K_d:'RIGHT',pygame.K_RIGHT:'RIGHT'}
                if e.key in moves:game.player.queued=moves[e.key]
                elif e.key==pygame.K_v:game.viz=not game.viz; prefs['show_paths']=game.viz
                elif e.key in (pygame.K_p,pygame.K_ESCAPE):state='PAUSE'
                elif e.key==pygame.K_r:game=Game(game.high,prefs['difficulty'],prefs['show_paths'])
            elif e.key==pygame.K_ESCAPE:state='MENU'
        if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            if state=='LAB' and lab_grid and lab_grid[0].collidepoint(e.pos):
                rect,tile=lab_grid; p=((e.pos[0]-rect.x)//tile,(e.pos[1]-rect.y)//tile); mods=pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:lab_start=p
                elif mods & pygame.KMOD_CTRL:lab_goal=p
                elif p not in (lab_start,lab_goal):
                    if p in lab_walls:lab_walls.remove(p)
                    else:lab_walls.add(p)
                lab_result=None
            for label,r,enabled in buttons:
                if enabled and r.collidepoint(e.pos):
                    if label=='PLAY':game=Game(prefs['high_score'],prefs['difficulty'],prefs['show_paths']); state='PLAY'
                    elif label=='AI LAB':state='LAB'
                    elif label=='HOW TO PLAY':state='HELP'
                    elif label=='SETTINGS':state='SETTINGS'
                    elif label=='CREDITS':state='CREDITS'
                    elif label=='QUIT':save_preferences(prefs); pygame.quit(); sys.exit()
                    elif label in ('BACK','MAIN MENU'):save_preferences({**prefs,'high_score':game.high if game else prefs['high_score']}); state='MENU'
                    elif label=='RESUME':state='PLAY'
                    elif label=='RESTART':game=Game(max(prefs['high_score'],game.high),prefs['difficulty'],prefs['show_paths']); state='PLAY'
                    elif label=='CHANGE DIFFICULTY':prefs['difficulty']=['EASY','MEDIUM','HARD'][(['EASY','MEDIUM','HARD'].index(prefs['difficulty'])+1)%3]
                    elif label=='TOGGLE DIAGNOSTICS':prefs['show_paths']=not prefs['show_paths']
                    elif label=='TOGGLE MUTE':prefs['muted']=not prefs['muted'];audio.muted=prefs['muted']
                    elif label=='RESET GRID':lab_walls={(4,y) for y in range(1,9) if y!=5}|{(x,6) for x in range(4,12) if x!=8}; lab_result=None
                    elif label.startswith('RUN'):run_lab(label)
    pygame.display.flip()
