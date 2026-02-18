import random

# grid size change these to make bigger or smol
R = 15
C = 15

dirs = [(-1,0),(0,1),(1,0),(1,1),(0,-1),(-1,-1)] # no diagnoalls top right or botom left
wall_chance = 0.03

def makegrid():
    g = []
    for i in range(R):
        r = []
        for j in range(C):
            r.append(0)
        g.append(r)
    return g

def addwalls(g, num=40):
    n = 0
    while n < num:
        x = random.randint(0,R-1)
        y = random.randint(0,C-1)
        if g[x][y]==0:
            g[x][y] = 1
            n+=1

def getnbrs(g, p):
    res = []
    for d in dirs:
        nx = p[0]+d[0]
        ny = p[1]+d[1]
        if nx>=0 and nx<R and ny>=0 and ny<C:
            if g[nx][ny] != 1:
                res.append((nx,ny))
    return res

def tryspawn(g, s, t):
    if random.random() < wall_chance:
        x = random.randint(0,R-1)
        y = random.randint(0,C-1)
        if g[x][y]==0 and (x,y)!=s and (x,y)!=t:
            g[x][y]=1
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
