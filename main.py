import pygame, sys, random, time
from gridstuff import makegrid, addwalls, tryspawn
from algoss import bfs,dfs,ucs,dls,iddfs,bidirectional, gbfs, astar

# --- User Input for Grid Setup ---
try:
    R = int(input("Enter grid rows (e.g., 25): "))
    C = int(input("Enter grid columns (e.g., 40): "))
    DENSITY = float(input("Enter wall density (e.g., 0.3): "))
except (ValueError, TypeError):
    print("Invalid input. Using defaults.")
    R, C, DENSITY = 25, 40, 0.3

pygame.init()
# colrs n stuff
BG = (240,240,235)
WALL_C = (40,40,40)
START_C = (30,180,30)
END_C = (200,40,40)
FRONT_C = (255, 255, 0) # Yellow
SEEN_C = (65, 105, 225) # Royal Blue
PATH_C = (50, 205, 50)  # Lime Green
AGENT_C = (128, 0, 128) # Purple
WHITE = (255,255,255)
TXT_C = (50,50,50)

sz = 20  # cell size
gap = 1
toparea = 55
botarea = 120
gw = C*(sz+gap)+gap
gh = R*(sz+gap)+gap
W = gw+180
H = toparea+gh+botarea
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Advanced Search Visualizer")
clock = pygame.time.Clock()

f1 = pygame.font.SysFont("arial",15)
f2 = pygame.font.SysFont("arial",19,bold=True)
f3 = pygame.font.SysFont("arial",12)
f4 = pygame.font.SysFont("arial",11)

# --- Algorithm and Heuristic Setup ---
algos = ["BFS","DFS","UCS","DLS","IDDFS","Bidirectional", "GBFS", "A*"]
algofn = [bfs,dfs,ucs,dls,iddfs,bidirectional, gbfs, astar]
selidx = 0

heuristics = ["Manhattan", "Euclidean"]
sel_heuristic_idx = 0
needs_heuristic = {"GBFS", "A*"}

# --- Grid and State Variables ---
g = makegrid(R, C)
sp = (R//4, C//4)
tp = (R*3//4, C*3//4)

# State variables
fr = set()
exp = set()
pth = None # The final path to be displayed statically
running = False # Is a search algorithm running?
gen = None
msg = "Select an algorithm and press 'Go' or edit the grid."

# New state for dynamic mode and traversal
dynamic_mode = False
agent_pos = None
path_to_follow = [] # The path the agent is currently following

# Metrics
nodes_visited = 0
path_cost = 0.0
exec_time = 0.0

def doreset():
    global g,fr,exp,pth,running,gen,msg, agent_pos, path_to_follow
    global nodes_visited, path_cost, exec_time
    g = makegrid(R, C)
    g[sp[0]][sp[1]]=2
    g[tp[0]][tp[1]]=3
    addwalls(g, sp, tp, density=DENSITY)
    g[sp[0]][sp[1]]=2
    g[tp[0]][tp[1]]=3
    fr=set(); exp=set(); pth=None
    running=False; gen=None
    agent_pos = None
    path_to_follow = []
    nodes_visited = 0
    path_cost = 0.0
    exec_time = 0.0
    msg="Grid reset! Select an algorithm and press 'Go'."

doreset() # Initial setup

def drawlegend():
    # legnd on right side
    lx = gw+25
    ly = toparea+10
    items = [
        (START_C, "Start Node"),
        (END_C, "Goal Node"),
        (WALL_C, "Wall/Obstacle"),
        (FRONT_C, "Frontier Node"),
        (SEEN_C, "Explored Node"),
        (PATH_C, "Final Path"),
        (AGENT_C, "Agent Position"),
    ]
    head = f1.render("Legend:",True,TXT_C)
    screen.blit(head,(lx,ly))
    ly+=25
    for color,label in items:
        pygame.draw.rect(screen,color,(lx,ly,16,16))
        pygame.draw.rect(screen,(180,180,180),(lx,ly,16,16),1)
        txt = f3.render(label,True,TXT_C)
        screen.blit(txt,(lx+22,ly+1))
        ly+=22

    # Metrics Dashboard
    ly+=15
    head = f1.render("Metrics:",True,TXT_C)
    screen.blit(head,(lx,ly))
    ly+=25
    metrics = [
        (f"Nodes Visited:", f"{nodes_visited}"),
        (f"Path Cost:", f"{path_cost:.2f}"),
        (f"Exec Time (ms):", f"{exec_time:.2f}"),
    ]
    for label, value in metrics:
        l_txt = f4.render(label, True, TXT_C)
        v_txt = f4.render(value, True, (100,60,60))
        screen.blit(l_txt, (lx, ly))
        screen.blit(v_txt, (lx + 95, ly))
        ly += 18

def drawgrid():
    screen.fill(BG)
    # title
    title = f2.render("Search Algo. By moho (23F-0677)",True,TXT_C)
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
            if agent_pos == p:
                co = AGENT_C
            elif pth and p in pth:
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

    pygame.display.flip()

def drawbuttons():
    by = toparea+gh+10
    mx,my = pygame.mouse.get_pos()
    is_interactive = not running and not path_to_follow

    # --- Algo Selection ---
    btns = getbtns()
    # Prev Algo
    c = (100,160,200) if btns['prev_algo'].collidepoint(mx,my) and is_interactive else (70,130,180)
    pygame.draw.rect(screen,c,btns['prev_algo'],border_radius=4)
    screen.blit(f1.render("<",True,WHITE),(btns['prev_algo'].centerx-4,btns['prev_algo'].centery-8))
    # Next Algo
    c = (100,160,200) if btns['next_algo'].collidepoint(mx,my) and is_interactive else (70,130,180)
    pygame.draw.rect(screen,c,btns['next_algo'],border_radius=4)
    screen.blit(f1.render(">",True,WHITE),(btns['next_algo'].centerx-4,btns['next_algo'].centery-8))
    # Algo Name
    screen.blit(f1.render(algos[selidx],True,TXT_C),(112,by+6))

    # --- Heuristic Selection ---
    if algos[selidx] in needs_heuristic:
        # Prev Heuristic
        c = (100,160,200) if btns['prev_heuristic'].collidepoint(mx,my) and is_interactive else (70,130,180)
        pygame.draw.rect(screen,c,btns['prev_heuristic'],border_radius=4)
        screen.blit(f1.render("<",True,WHITE),(btns['prev_heuristic'].centerx-4,btns['prev_heuristic'].centery-8))
        # Next Heuristic
        c = (100,160,200) if btns['next_heuristic'].collidepoint(mx,my) and is_interactive else (70,130,180)
        pygame.draw.rect(screen,c,btns['next_heuristic'],border_radius=4)
        screen.blit(f1.render(">",True,WHITE),(btns['next_heuristic'].centerx-4,btns['next_heuristic'].centery-8))
        # Heuristic Name
        screen.blit(f1.render(heuristics[sel_heuristic_idx],True,TXT_C),(300,by+6))

    # --- Control Buttons ---
    # Go
    c = (60,190,60) if btns['go'].collidepoint(mx,my) and is_interactive else (40,160,40)
    pygame.draw.rect(screen,c,btns['go'],border_radius=4)
    screen.blit(f1.render("Go",True,WHITE),(btns['go'].centerx-8,btns['go'].centery-8))
    # Reset
    c = (230,140,50) if btns['reset'].collidepoint(mx,my) else (210,120,30)
    pygame.draw.rect(screen,c,btns['reset'],border_radius=4)
    screen.blit(f1.render("Reset",True,WHITE),(btns['reset'].x+6,btns['reset'].centery-8))

    # --- Dynamic Mode Toggle ---
    by2 = toparea+gh+80
    c = (60,190,60) if dynamic_mode else (200,60,60)
    if btns['dynamic'].collidepoint(mx,my) and is_interactive: c = (c[0], c[1]+30, c[2])
    pygame.draw.rect(screen,c,btns['dynamic'],border_radius=4)
    label = "Dynamic: ON" if dynamic_mode else "Dynamic: OFF"
    screen.blit(f1.render(label,True,WHITE),(btns['dynamic'].x+8,btns['dynamic'].centery-8))

def getbtns():
    by = toparea+gh+10
    by2 = toparea+gh+80
    return {
        'prev_algo': pygame.Rect(12,by,40,30), 'next_algo': pygame.Rect(60,by,40,30),
        'prev_heuristic': pygame.Rect(200,by,40,30), 'next_heuristic': pygame.Rect(248,by,40,30),
        'go': pygame.Rect(420,by,55,30), 'reset': pygame.Rect(485,by,65,30),
        'dynamic': pygame.Rect(12,by2,110,30)
    }

def screen_to_grid(pos):
    ox, oy = 10, toparea
    r = (pos[1] - oy) // (sz + gap)
    c = (pos[0] - ox) // (sz + gap)
    if 0 <= r < R and 0 <= c < C:
        return r, c
    return None

def startgo(start_node=None):
    global gen,running,fr,exp,pth,msg, agent_pos, path_to_follow, _start_time
    current_start = start_node if start_node else sp
    fr=set([current_start]); exp=set(); pth=None; path_to_follow=[]; agent_pos=None

    fn = algofn[selidx]
    algo_name = algos[selidx]
    
    args = [g, current_start, tp]
    if algo_name in needs_heuristic:
        args.append(heuristics[sel_heuristic_idx].lower())
    elif algo_name == "DLS": args.append(R*C//4)
    elif algo_name == "IDDFS": args.append(R+C)

    gen = fn(*args)
    running=True
    msg=f"Running {algo_name}..."
    _start_time = time.perf_counter()

def dostep():
    global fr,exp,pth,running,msg,gen, agent_pos, path_to_follow
    global nodes_visited, path_cost, exec_time
    if gen is None: return
    try:
        f,e,path,cost,visited = next(gen)
        fr = set(f)
        exp = e
        if path is not None: # Search is finished
            _end_time = time.perf_counter()
            exec_time = (_end_time - _start_time) * 1000
            nodes_visited = visited if visited is not None else len(e)
            path_cost = cost if cost is not None else 0.0

            if path:
                if dynamic_mode:
                    path_to_follow = path
                    agent_pos = path[0]
                    msg = f"Path found ({len(path)} steps). Traversing..."
                else:
                    pth = set(path)
                    msg = f"{algos[selidx]} path length: {len(path)}, Cost: {path_cost:.2f}"
            else:
                pth = None
                msg = f"{algos[selidx]} could not find a path."
            running = False
            gen = None
    except StopIteration:
        running=False
        if pth is None and not path_to_follow:
            msg = f"{algos[selidx]} no path found."
        gen = None

def traverse_step():
    global agent_pos, path_to_follow, msg
    if not path_to_follow: return

    path_to_follow.pop(0)
    if not path_to_follow:
        agent_pos = tp
        msg = "Goal reached!"
        return
    
    agent_pos = path_to_follow[0]
    new_wall = tryspawn(g, sp, tp, agent_pos)

    if new_wall and new_wall in path_to_follow:
        msg = f"Path blocked at {new_wall}! Re-planning..."
        path_to_follow = []
        startgo(start_node=agent_pos)

# main loop
last = 0
spd = 25  # miliseconds between steps
while True:
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        is_interactive = not running and not path_to_follow

        if ev.type==pygame.MOUSEBUTTONDOWN:
            pos = ev.pos
            btns = getbtns()
            if is_interactive:
                if btns['prev_algo'].collidepoint(pos): selidx = (selidx-1) % len(algos)
                elif btns['next_algo'].collidepoint(pos): selidx = (selidx+1) % len(algos)
                elif btns['go'].collidepoint(pos): startgo()
                elif algos[selidx] in needs_heuristic and btns['prev_heuristic'].collidepoint(pos): sel_heuristic_idx = (sel_heuristic_idx-1) % len(heuristics)
                elif algos[selidx] in needs_heuristic and btns['next_heuristic'].collidepoint(pos): sel_heuristic_idx = (sel_heuristic_idx+1) % len(heuristics)
                elif btns['dynamic'].collidepoint(pos): dynamic_mode = not dynamic_mode
                else: # Grid editing
                    grid_pos = screen_to_grid(pos)
                    if grid_pos and grid_pos != sp and grid_pos != tp:
                        if ev.button == 1: g[grid_pos[0]][grid_pos[1]] = 1 # Add wall
                        elif ev.button == 3: g[grid_pos[0]][grid_pos[1]] = 0 # Remove wall
            if btns['reset'].collidepoint(pos): doreset()

        if ev.type==pygame.KEYDOWN:
            if ev.key==pygame.K_SPACE and is_interactive: startgo()
            if ev.key==pygame.K_r: doreset()

    t = pygame.time.get_ticks()
    if t-last > spd:
        if running: dostep()
        elif dynamic_mode and path_to_follow: traverse_step()
        last = t

    drawgrid()
    clock.tick(60)