def mark_empty(grid, x, y):
    try:
        if not grid[x][y]:
            return
    except LookupError:
        return False
    if x < 0 or y < 0:
        return
    grid[x][y] = False
    mark_empty(grid, x + 1, y)

    mark_empty(grid, x - 1, y)

    mark_empty(grid, x, y + 1)

    mark_empty(grid, x, y - 1)

    return True
    
def get_spots(grid):

    spots = 0

    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if not cell:
                continue
            spots += 1
            mark_empty(grid, r, c)

    return spots


def group(grid):

    grid = [[True if c == 'Y' else False for c in row] for row in grid]

    avail_spots = get_spots(grid)
    print (avail_spots)
    return len(comb_with_even_sheeps)

grid = group(['YNNY', 'NYNY',  'NYNN','NYNN','NYNN','NYNN','YNNY'])
get_field(grid)