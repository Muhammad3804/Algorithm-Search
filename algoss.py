from collections import deque
import heapq
from gridstuff import getnbrs, tryspawn, tracepath

def bfs(grid, s, t):
    q = deque([s])
    seen = set([s])
    par = {}
    fr = {s}
    while q:
        c = q.popleft()
        fr.discard(c)
        if c==t:
            yield list(fr),seen,tracepath(par,s,t)
            return
        for n in getnbrs(grid,c):
            if n not in seen:
                seen.add(n)
                par[n]=c
                q.append(n)
                fr.add(n)
        tryspawn(grid,s,t)
        # remove blockd
        tmp = []
        for x in list(q):
            if grid[x[0]][x[1]]!=0 and x!=s and x!=t: tmp.append(x)
        for x in tmp:
            q.remove(x)
            fr.discard(x)
        yield list(fr),seen.copy(),None
    yield [],seen.copy(),[]

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
            yield list(fr),seen,tracepath(par,s,t)
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
        yield list(fr),seen.copy(),None
    yield [],seen.copy(),[]

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
            yield list(fr),seen,tracepath(par,s,t)
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
        yield list(fr),seen.copy(),None
    yield [],seen.copy(),[]

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
            yield list(fr),seen,tracepath(par,s,t)
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
        yield list(fr),seen.copy(),None
    yield [],seen.copy(),[]

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
                yield list(fr),allseen,tracepath(par,s,t)
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
            yield list(fr),allseen.copy(),None
    yield [],allseen.copy(),[]

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
                pth = _bipath(p1,p2,s,t,c)
                yield list(fr),v1|v2,pth
                return
            for n in getnbrs(grid,c):
                if n not in v1:
                    v1.add(n); p1[n]=c; q1.append(n); fr.add(n)
        if q2:
            c = q2.popleft()
            fr.discard(c)
            if c in v1:
                pth = _bipath(p1,p2,s,t,c)
                yield list(fr),v1|v2,pth
                return
            for n in getnbrs(grid,c):
                if n not in v2:
                    v2.add(n); p2[n]=c; q2.append(n); fr.add(n)
        tryspawn(grid,s,t)
        for qq in [q1,q2]:
            bad = [x for x in qq if grid[x[0]][x[1]]!=0 and x!=s and x!=t]
            for x in bad:
                qq.remove(x); fr.discard(x)
        yield list(fr),(v1|v2).copy(),None
    yield [],(v1|v2).copy(),[]

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