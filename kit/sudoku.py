import random, json, sys

def valid(b, r, c, v):
    for i in range(9):
        if b[r][i] == v or b[i][c] == v:
            return False
    br, bc = 3 * (r // 3), 3 * (c // 3)
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if b[i][j] == v:
                return False
    return True

def fill(b):
    for r in range(9):
        for c in range(9):
            if b[r][c] == 0:
                vals = list(range(1, 10)); random.shuffle(vals)
                for v in vals:
                    if valid(b, r, c, v):
                        b[r][c] = v
                        if fill(b):
                            return True
                        b[r][c] = 0
                return False
    return True

def count(b, limit=2):
    for r in range(9):
        for c in range(9):
            if b[r][c] == 0:
                n = 0
                for v in range(1, 10):
                    if valid(b, r, c, v):
                        b[r][c] = v
                        n += count(b, limit - n)
                        b[r][c] = 0
                        if n >= limit:
                            return n
                return n
    return 1

def make(clues, seed):
    random.seed(seed)
    sol = [[0] * 9 for _ in range(9)]
    fill(sol)
    puz = [row[:] for row in sol]
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    filled = 81
    for r, c in cells:
        if filled <= clues:
            break
        keep = puz[r][c]
        puz[r][c] = 0
        if count([row[:] for row in puz]) != 1:
            puz[r][c] = keep
        else:
            filled -= 1
    return puz, sol, filled

if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20261015
    out = []
    for i, (label, clues) in enumerate([("Medium", 32), ("Hard", 25)]):
        p, s, f = make(clues, seed + i)
        out.append({"label": label, "puzzle": p, "solution": s, "clues": f})
    print(json.dumps(out))
