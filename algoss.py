from collections import deque
import heapq
import math
from gridstuff import getnbrs, tryspawn, tracepath

# --- Heuristic Functions ---

def _manhattan_distance(p1, p2):
    """Helper function for Manhattan distance: |x1 - x2| + |y1 - y2|"""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def _euclidean_distance(p1, p2):
    """Helper function for Euclidean distance: sqrt((x1 - x2)^2 + (y1 - y2)^2)"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def heuristic(p1, p2, heuristic_type="manhattan"):
    """
    Dispatches to the selected heuristic function based on a string identifier.

    Args:
        p1 (tuple): The first point (row, col).
        p2 (tuple): The second point (row, col).
        heuristic_type (str): The type of heuristic to use ("manhattan" or "euclidean").

    Returns:
        float: The calculated heuristic value.
    """
    if heuristic_type.lower() == "euclidean":
        return _euclidean_distance(p1, p2)
    # Default to Manhattan for safety and speed
    return _manhattan_distance(p1, p2)

def bfs(grid, s, t):
    q = deque([s])
    seen = set([s])
    par = {}
    fr = {s}
    R, C = len(grid), len(grid[0])
    while q:
        c = q.popleft()
        fr.discard(c)
        if c==t:
            path = tracepath(par,s,t)
            yield list(fr),seen,path,len(path)-1 if path else 0,len(seen)
            return
        for n in getnbrs(grid,c):
            if n not in seen:
                seen.add(n)
                par[n]=c
                q.append(n)
                fr.add(n)
        tryspawn(grid,s,t)
        # remove blocked
        tmp = []
        for x in list(q):
            if grid[x[0]][x[1]]!=0 and x!=s and x!=t: tmp.append(x)
        for x in tmp:
            q.remove(x)
            fr.discard(x)
        yield list(fr),seen.copy(),None,None,None
    yield [],seen.copy(),[],0,len(seen)

def dfs(grid, s, t):
    stk = [s]
    seen = set()
    par = {}
    fr = {s}
    while stk:
        c = stk.pop()
        fr.discard(c)
        if c in seen: continue
        seen.add(c)
        if c==t:
            path = tracepath(par,s,t)
            yield list(fr),seen,path,len(path)-1 if path else 0,len(seen)
            return
        for n in reversed(getnbrs(grid,c)):
            if n not in seen:
                par[n]=c
                stk.append(n)
                fr.add(n)
        tryspawn(grid,s,t)
        ns = []
        for x in stk:
            if grid[x[0]][x[1]]==0 or x==s or x==t:
                ns.append(x)
            else: fr.discard(x)
        stk = ns
        yield list(fr),seen.copy(),None,None,None
    yield [],seen.copy(),[],0,len(seen)

def ucs(grid, s, t):
    idx = 0
    hp = [(0,idx,s)]
    idx+=1
    seen = set()
    par = {}
    cst = {s:0}
    fr = {s}
    while hp:
        w,_,c = heapq.heappop(hp)
        fr.discard(c)
        if c in seen: continue
        seen.add(c)
        if c==t:
            path = tracepath(par,s,t)
            yield list(fr),seen,path,cst.get(t, 0),len(seen)
            return
        for n in getnbrs(grid,c):
            dx = abs(n[0]-c[0])
            dy = abs(n[1]-c[1])
            cost = 1.4 if (dx==1 and dy==1) else 1.0
            nw = w+cost
            if n not in cst or nw<cst[n]:
                cst[n]=nw
                par[n]=c
                heapq.heappush(hp,(nw,idx,n))
                idx+=1
                fr.add(n)
        tryspawn(grid,s,t)
        nh = []
        for it in hp:
            if grid[it[2][0]][it[2][1]]==0 or it[2]==s or it[2]==t:
                nh.append(it)
            else: fr.discard(it[2])
        heapq.heapify(nh)
        hp = nh
        yield list(fr),seen.copy(),None,None,None
    yield [],seen.copy(),[],0,len(seen)

def dls(grid, s, t, limit=20):
    seen = set()
    par = {}
    fr = set()
    stk = [(s,0)]
    fr.add(s)
    while stk:
        c,d = stk.pop()
        fr.discard(c)
        if c in seen: continue
        seen.add(c)
        if c==t:
            path = tracepath(par,s,t)
            yield list(fr),seen,path,len(path)-1 if path else 0,len(seen)
            return
        if d<limit:
            for n in reversed(getnbrs(grid,c)):
                if n not in seen:
                    par[n]=c
                    stk.append((n,d+1))
                    fr.add(n)
        tryspawn(grid,s,t)
        ns = []
        for x,dd in stk:
            if grid[x[0]][x[1]]==0 or x==s or x==t:
                ns.append((x,dd))
            else: fr.discard(x)
        stk=ns
        yield list(fr),seen.copy(),None,None,None
    yield [],seen.copy(),[],0,len(seen)

# iteratve deepenning
def iddfs(grid, s, t, max_depth=30):
    allseen = set()
    for lim in range(max_depth+1):
        seen = set()
        par = {}
        stk = [(s,0)]
        fr = set([s])
        while stk:
            c,d = stk.pop()
            fr.discard(c)
            if c in seen: continue
            seen.add(c)
            allseen.add(c)
            if c==t:
                path = tracepath(par,s,t)
                yield list(fr),allseen,path,len(path)-1 if path else 0,len(allseen)
                return
            if d<lim:
                for n in reversed(getnbrs(grid,c)):
                    if n not in seen:
                        par[n]=c
                        stk.append((n,d+1))
                        fr.add(n)
            tryspawn(grid,s,t)
            ns = []
            for x,dd in stk:
                if grid[x[0]][x[1]]==0 or x==s or x==t:
                    ns.append((x,dd))
                else: fr.discard(x)
            stk=ns
            yield list(fr),allseen.copy(),None,None,None
    yield [],allseen.copy(),[],0,len(allseen)

def bidirectional(grid, s, t):
    q1 = deque([s])
    q2 = deque([t])
    v1 = {s}
    v2 = {t}
    p1 = {}
    p2 = {}
    fr = {s,t}
    while q1 or q2:
        if q1:
            c = q1.popleft()
            fr.discard(c)
            if c in v2:
                path = _bipath(p1,p2,s,t,c)
                cost = len(path)-1 if path else 0
                yield list(fr),v1|v2,path,cost,len(v1|v2)
                return
            for n in getnbrs(grid,c):
                if n not in v1:
                    v1.add(n); p1[n]=c; q1.append(n); fr.add(n)
        if q2:
            c = q2.popleft()
            fr.discard(c)
            if c in v1:
                path = _bipath(p1,p2,s,t,c)
                cost = len(path)-1 if path else 0
                yield list(fr),v1|v2,path,cost,len(v1|v2)
                return
            for n in getnbrs(grid,c):
                if n not in v2:
                    v2.add(n); p2[n]=c; q2.append(n); fr.add(n)
        tryspawn(grid,s,t)
        for qq in [q1,q2]:
            bad = [x for x in qq if grid[x[0]][x[1]]!=0 and x!=s and x!=t]
            for x in bad:
                qq.remove(x); fr.discard(x)
        yield list(fr),(v1|v2).copy(),None,None,None
    yield [],(v1|v2).copy(),[],0,len(v1|v2)

def _bipath(p1,p2,s,t,m):
    a = []
    n = m
    while n!=s:
        a.append(n)
        if n not in p1: return []
        n=p1[n]
    a.append(s)
    a.reverse()
    b = []
    n = m
    while n!=t:
        if n not in p2: return []
        n=p2[n]
        b.append(n)
    return a+b

def gbfs(grid, s, t, heuristic_type="manhattan"):
    idx = 0
    h = heuristic(s, t, heuristic_type)
    hp = [(h, idx, s)]
    idx += 1
    seen = set()
    par = {}
    fr = {s}

    while hp:
        _, _, c = heapq.heappop(hp)
        fr.discard(c)
        if c in seen:
            continue
        seen.add(c)

        if c == t:
            path = tracepath(par, s, t)
            final_cost = 0
            if path:
                for i in range(len(path) - 1):
                    p1, p2 = path[i], path[i+1]
                    dx, dy = abs(p1[0]-p2[0]), abs(p1[1]-p2[1])
                    final_cost += 1.4 if (dx==1 and dy==1) else 1.0
            yield list(fr), seen, path, final_cost, len(seen)
            return

        for n in getnbrs(grid, c):
            if n not in seen:
                par[n] = c
                h = heuristic(n, t, heuristic_type)
                heapq.heappush(hp, (h, idx, n))
                idx += 1
                fr.add(n)

        tryspawn(grid, s, t)
        nh = []
        for it in hp:
            if grid[it[2][0]][it[2][1]] == 0 or it[2] == s or it[2] == t:
                nh.append(it)
            else:
                fr.discard(it[2])
        heapq.heapify(nh)
        hp = nh
        yield list(fr), seen.copy(), None, None, None

    yield [], seen.copy(), [], 0, len(seen)


def astar(grid, s, t, heuristic_type="manhattan"):
    idx = 0
    g_cost = {s: 0}
    f_cost = {s: heuristic(s, t, heuristic_type)}
    hp = [(f_cost[s], idx, s)]
    idx += 1
    seen = set()
    par = {}
    fr = {s}

    while hp:
        _, _, c = heapq.heappop(hp)
        fr.discard(c)

        if c in seen:
            continue
        seen.add(c)

        if c == t:
            path = tracepath(par, s, t)
            yield list(fr), seen, path, g_cost.get(t, 0), len(seen)
            return

        for n in getnbrs(grid, c):
            dx, dy = abs(n[0]-c[0]), abs(n[1]-c[1])
            cost = 1.4 if (dx==1 and dy==1) else 1.0
            new_g_cost = g_cost[c] + cost

            if n not in g_cost or new_g_cost < g_cost[n]:
                g_cost[n] = new_g_cost
                f_cost[n] = new_g_cost + heuristic(n, t, heuristic_type)
                par[n] = c
                heapq.heappush(hp, (f_cost[n], idx, n))
                idx += 1
                fr.add(n)

        tryspawn(grid, s, t)
        nh = []
        for it in hp:
            if grid[it[2][0]][it[2][1]] == 0 or it[2] == s or it[2] == t:
                nh.append(it)
            else: fr.discard(it[2])
        heapq.heapify(nh)
        hp = nh
        yield list(fr), seen.copy(), None, None, None

    yield [], seen.copy(), [], 0, len(seen)