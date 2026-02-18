import pygame, sys, random
from gridstuff import R, C, makegrid, addwalls
from algoss import bfs,dfs,ucs,dls,iddfs,bidirectional

pygame.init()
# colrs n stuff
BG = (240,240,235)
WALL_C = (40,40,40)
START_C = (30,180,30)
END_C = (200,40,40)
FRONT_C = (80,130,230)
SEEN_C = (190,190,190)
PATH_C = (255,210,50)
WHITE = (255,255,255)
TXT_C = (50,50,50)

sz = 26  # cell size
gap = 2
toparea = 55
botarea = 90
gw = C*(sz+gap)+gap
gh = R*(sz+gap)+gap
W = gw+120
H = toparea+gh+botarea
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("search algos")
clock = pygame.time.Clock()

f1 = pygame.font.SysFont("arial",15)
f2 = pygame.font.SysFont("arial",19,bold=True)
f3 = pygame.font.SysFont("arial",12)
f4 = pygame.font.SysFont("arial",10)

algos = ["BFS","DFS","UCS","DLS","IDDFS","Bidirectional"]
algofn = [bfs,dfs,ucs,dls,iddfs,bidirectional]
selidx = 0

# makin grid
g = makegrid()
sp = (1,1)
tp = (R-2,C-2)
g[sp[0]][sp[1]] = 2
g[tp[0]][tp[1]] = 3
addwalls(g, 55)
g[sp[0]][sp[1]] = 2 
g[tp[0]][tp[1]] = 3

# statess
fr = set()
exp = set()
pth = None
running = False
gen = None
msg = "select algo u want!!"

def drawlegend():
    # legnd on right side
    lx = gw+25
    ly = toparea+10
    items = [
        (START_C, "start"),
        (END_C, "endd"),
        (WALL_C, "wall"),
        (FRONT_C, "front"),
        (SEEN_C, "explored"),
        (PATH_C, "path found"),
    ]
    head = f1.render("info:",True,TXT_C)
    screen.blit(head,(lx,ly))
    ly+=25
    for color,label in items:
        pygame.draw.rect(screen,color,(lx,ly,16,16))
        pygame.draw.rect(screen,(180,180,180),(lx,ly,16,16),1)
        txt = f3.render(label,True,TXT_C)
        screen.blit(txt,(lx+22,ly+1))
        ly+=24
    # show currnt algo info
    ly+=10
    info = f3.render("current algo: "+algos[selidx],True,(100,60,60))
    screen.blit(info,(lx,ly))

def drawgrid():
    screen.fill(BG)
    # title
    title = f2.render("Search Algo. By moho & cultriq(23F-0677 & 23F-0836)",True,TXT_C)
    screen.blit(title,(10,12))
    # draw the grid
    ox = 10
    oy = toparea
    for i in range(R):
        for j in range(C):
            x = ox+j*(sz+gap)+gap
            y = oy+i*(sz+gap)+gap
            p = (i,j)
            v = g[i][j]
            # pick color
            if pth and p in pth:
                co = PATH_C
            elif p==sp:
                co = START_C
            elif p==tp:
                co = END_C
            elif v==1:
                co = WALL_C
            elif p in exp:
                co = SEEN_C
            elif p in fr:
                co = FRONT_C
            else:
                co = WHITE
            pygame.draw.rect(screen,co,(x,y,sz,sz))
            pygame.draw.rect(screen,(200,200,200),(x,y,sz,sz),1)
    drawlegend()
    # btns
    drawbuttons()

    # msg
    m = f3.render(msg,True,TXT_C)
    screen.blit(m,(12,toparea+gh+50))

    # credits
    cr = f4.render("made by moho & cultriq (23F-0677 & 23F-0836)",True,(150,150,150))
    screen.blit(cr,(W//2-cr.get_width()//2, H-14))
    pygame.display.flip()

def drawbuttons():
    by = toparea+gh+10
    mx,my = pygame.mouse.get_pos()

    # prev btn
    b1 = pygame.Rect(12,by,40,30)
    c1 = (100,160,200) if b1.collidepoint(mx,my) else (70,130,180)
    pygame.draw.rect(screen,c1,b1,border_radius=4)
    screen.blit(f1.render("<",True,WHITE),(b1.centerx-4,b1.centery-8))

    # next btn
    b2 = pygame.Rect(60,by,40,30)
    c2 = (100,160,200) if b2.collidepoint(mx,my) else (70,130,180)
    pygame.draw.rect(screen,c2,b2,border_radius=4)
    screen.blit(f1.render(">",True,WHITE),(b2.centerx-4,b2.centery-8))

    # algo name between
    nm = f1.render(algos[selidx],True,TXT_C)
    screen.blit(nm,(112,by+6))

    # go btn
    b3 = pygame.Rect(220,by,55,30)
    c3 = (60,190,60) if b3.collidepoint(mx,my) else (40,160,40)
    pygame.draw.rect(screen,c3,b3,border_radius=4)
    screen.blit(f1.render("Go",True,WHITE),(b3.centerx-8,b3.centery-8))

    # reset
    b4 = pygame.Rect(285,by,55,30)
    c4 = (230,140,50) if b4.collidepoint(mx,my) else (210,120,30)
    pygame.draw.rect(screen,c4,b4,border_radius=4)
    screen.blit(f1.render("Reset",True,WHITE),(b4.x+6,b4.centery-8))

def getbtns():
    by = toparea+gh+10
    return (pygame.Rect(12,by,40,30),pygame.Rect(60,by,40,30),
            pygame.Rect(220,by,55,30),pygame.Rect(285,by,55,30))

def doreset():
    global g,fr,exp,pth,running,gen,msg
    g = makegrid()
    g[sp[0]][sp[1]]=2
    g[tp[0]][tp[1]]=3
    addwalls(g,55)
    g[sp[0]][sp[1]]=2
    g[tp[0]][tp[1]]=3
    fr=set(); exp=set(); pth=None
    running=False; gen=None
    msg="grid reset! pick algo n press go"

def startgo():
    global gen,running,fr,exp,pth,msg
    fr=set(); exp=set(); pth=None
    fn = algofn[selidx]
    if selidx==3:  # dls
        gen = fn(g,sp,tp,limit=25)
    elif selidx==4:  # iddfs
        gen = fn(g,sp,tp,max_depth=35)
    else:
        gen = fn(g,sp,tp)
    running=True
    msg="running "+algos[selidx]+"..."

def dostep():
    global fr,exp,pth,running,msg,gen
    if gen==None: return
    try:
        f,e,path = next(gen)
        fr = set(f)
        exp = e
        if path != None:
            if len(path)>0:
                pth = set(path)
                msg = algos[selidx]+"path length="+str(len(path))
            else:
                pth = None
                msg = algos[selidx]+" cant find path :("
            running = False
    except StopIteration:
        running=False
        if pth==None:
            msg = algos[selidx]+" no path found"

# main loop
last = 0
spd = 55  # miliseconds between steps
while True:
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
        if ev.type==pygame.MOUSEBUTTONDOWN:
            x,y = ev.pos
            b1,b2,b3,b4 = getbtns()
            if b1.collidepoint(x,y) and not running:
                selidx = (selidx-1) % len(algos)
                msg = "picked: "+algos[selidx]
            elif b2.collidepoint(x,y) and not running:
                selidx = (selidx+1) % len(algos)
                msg = "picked: "+algos[selidx]
            elif b3.collidepoint(x,y) and not running:
                startgo()
            elif b4.collidepoint(x,y):
                doreset()
        if ev.type==pygame.KEYDOWN:
            if ev.key==pygame.K_SPACE and not running:
                startgo()
            if ev.key==pygame.K_r:
                doreset()
    t = pygame.time.get_ticks()
    if running and t-last > spd:
        dostep()
        last = t
    drawgrid()
    clock.tick(60)