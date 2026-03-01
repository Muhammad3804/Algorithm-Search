import random

dirs = [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1), (1, 1)] # 8 directions
wall_chance = 0.05

def makegrid(R, C):
    g = []
    for i in range(R):
        r = []
        for j in range(C):
            r.append(0)
        g.append(r)
    return g

def addwalls(g, s, t, density=0.3):
    R, C = len(g), len(g[0])
    for r in range(R):
        for c in range(C):
            if (r, c) != s and (r, c) != t:
                if random.random() < density:
                    g[r][c] = 1

def getnbrs(g, p):
    res = []
    R, C = len(g), len(g[0])
    for d in dirs:
        nx, ny = p[0]+d[0], p[1]+d[1]
        if nx>=0 and nx<R and ny>=0 and ny<C:
            if g[nx][ny] != 1:
                res.append((nx,ny))
    return res

def tryspawn(g, s, t, agent_pos=None):
    R, C = len(g), len(g[0])
    if random.random() < wall_chance:
        for _ in range(10): # Try a few times to find a valid spot
            x, y = random.randint(0,R-1), random.randint(0,C-1)
            if g[x][y]==0 and (x,y)!=s and (x,y)!=t and (x,y)!=agent_pos:
                g[x][y]=1
                return (x,y) # Return new wall position
    return None

def tracepath(par, s, t):
    p = []
    n = t
    while n != s:
        p.append(n)
        if n not in par:
            return []
        n = par[n]
    p.append(s)
    p.reverse()
    return p
