from copy import deepcopy

probfour = 0.1

ex = [[1,0,1,2],[1,2,1,0],[2,0,2,0],[1,2,2,2]]

mem = dict()
val = dict()

def grid(width,height):
    return [[0 for i in range(width)] for j in range(height)]

def printgrid(grid):
    for line in grid:
        for cell in line:
            print(cell,end=' ')
        print()
    pass

def serialize(grid):
    s = [len(grid[0]),len(grid),]
    for line in grid:
        for cell in line:
            s.append(cell)
    return tuple(s)

def deserialize(sgrid):
    if sgrid == 'I':
        return 'I'
    g = grid(sgrid[0],sgrid[1])
    i = 2
    for a in range(len(g)):
        for b in range(len(g[0])):
            g[a][b] = sgrid[i]
            i += 1
    return g

def freecells(grid):
    frees=set()
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x]==0:
                frees.add((y,x))
    return frees

def transpose(og):
    ng = grid(len(og),len(og[0]))
    for y in range(len(og)):
        for x in range(len(og[0])):
            ng[x][y] = og[y][x]
    return ng

def reflect(og):
    return [[og[y][len(og[0])-x-1] for x in range(len(og[0]))] for y in range(len(og))]

def moveright(og):
    ng = deepcopy(og)
    if len(ng[0]) < 2:
        return [0,ng]
    score = 0
    for line in ng:
        end = len(line) - 1
        outer = end - 1
        while outer >= 0:
            inner = outer
            while inner < end:
                if (line[inner] > 0) and (line[inner+1] == 0):
                    line[inner+1] = line[inner]
                    line[inner] = 0
                elif (line[inner] > 0) and (line[inner+1] == line[inner]):
                    line[inner+1] += 1
                    line[inner] = 0
                    score += 2**line[inner+1]
                    end -= 1
                elif (line[inner] > 0):
                    end -= 1
                inner += 1
            outer -= 1
    return [score,ng]

def move(og, dir):
    if dir == "right":
        a = moveright(og)
        return [a[0],a[1]]
    elif dir == "left":
        a = moveright(reflect(og))
        return [a[0],reflect(a[1])]
    elif dir == "down":
        a = moveright(transpose(og))
        return [a[0],transpose(a[1])]
    elif dir == "up":
        a = moveright(reflect(transpose(og)))
        return [a[0],transpose(reflect(a[1]))]
    else:
        return "invalid direction"

def allowedmoves(gr):
    return tuple(x for x in ("right","left","up","down") if move(gr,x)[1]!=gr)

def canonize(gr):
    l = [gr,]
    l.append(reflect(gr))
    l.append(transpose(gr))
    l.append(reflect(transpose(gr)))
    l.append(transpose(reflect(gr)))
    l.append(reflect(transpose(reflect(gr))))
    l.append(transpose(reflect(transpose(gr))))
    l.append(reflect(transpose(reflect(transpose(gr)))))
    l.sort()
    return l[0]

def ndspawn(gr,p):
    d = dict()
    f = freecells(gr)
    l = len(freecells(gr))
    for coord in f:
        if p > 0.0:
            a2 = deepcopy(gr)
            a2[coord[0]][coord[1]] = 2
            a2 = serialize(canonize(a2))
            if a2 in d:
                d[a2] += p/l
            else:
                d[a2] = p/l
        if p < 1.0:
            a1 = deepcopy(gr)
            a1[coord[0]][coord[1]] = 1
            a1 = serialize(canonize(a1))
            if a1 in d:
                d[a1] += (1-p)/l
            else:
                d[a1] = (1-p)/l
    return d

def expand(sgrid,p):
    t = tuple(sorted(sgrid[:2]))
    t = t + (p,)
    global mem
    if t not in mem:
        mem[t] = dict()
    if sgrid in mem[t]:
        return None
    else:
        gr = deserialize(sgrid)
        allowed = allowedmoves(gr)
        immsucc = dict((serialize(canonize(move(gr,dir)[1])),move(gr,dir)[0]) for dir in allowed)
        mem[t][sgrid] = dict((a,[immsucc[a],ndspawn(deserialize(a),p)]) for a in immsucc)
        if len(mem[t][sgrid]) > 0:
            for a in mem[t][sgrid]:
                for s in mem[t][sgrid][a][1]:
                    expand(s,p)
        return None

def initialize(w,h,p):
    global mem
    t = tuple(sorted((w,h)))
    t = t + (p,)
    if t not in mem:
        mem[t] = dict()
    if "I" in mem[t]:
        return None
    g = canonize(grid(w,h))
    first = ndspawn(g,p)
    second = dict((s,ndspawn(deserialize(s),p)) for s in first)
    d = dict()
    for f in second:
        for s in second[f]:
            if s in d:
                d[s] += first[f] * second[f][s]
            else:
                d[s] = first[f] * second[f][s]
    mem[t]["I"] = {serialize(g):[0,d]}
    for x in d:
        expand(x,p)
    return None

def evaluate(t, sg):
    global val
    if t not in val:
        val[t] = dict()
    if sg in val[t]:
        return val[t][sg][1]
    if (t not in mem) or (sg not in mem[t]):
        if sg == 'I':
            initialize(*t)
        else:
            expand(sg,t[2])
    if len(mem[t][sg])==0:
        val[t][sg] = (None,0)
        return 0
    all = dict((a,mem[t][sg][a][0]+sum(evaluate(t,s)*mem[t][sg][a][1][s] for s in mem[t][sg][a][1])) for a in mem[t][sg])
    m = max(all, key=(lambda key: all[key]))
    val[t][sg] = (m,all[m])
    return all[m]