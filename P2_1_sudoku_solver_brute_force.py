import copy

puzzle = [[5,3,0,0,7,0,0,0,0],
          [6,0,0,1,9,5,0,0,0],
          [0,9,8,0,0,0,0,6,0],
          [8,0,0,0,6,0,0,0,3],
          [4,0,0,8,0,3,0,0,1],
          [7,0,0,0,2,0,0,0,6],
          [0,6,0,0,0,0,2,8,0],
          [0,0,0,4,1,9,0,0,5],
          [0,0,0,0,8,0,0,0,0]]


def possible(y, x, n, puzzle):
    # helper function
    for i in range(9):
        if puzzle[y][i] == n: return False
    for j in range(9):
        if puzzle[j][x] == n: return False
    x0 = (x // 3) * 3
    y0 = (y // 3) * 3
    for i in range(3):
        for j in range(3):
            if puzzle[y0 + i][x0 + j] == n: return False
    return True


def sudoku1(puzzle):
    # return all solutions found
    res = []
    def solve():
        for y in range(9):
            for x in range(9):
                if puzzle[y][x] == 0:
                    for n in range(1, 10):
                        if possible(y, x, n, puzzle):
                            puzzle[y][x] = n
                            solve()
                            puzzle[y][x] = 0
                    return
        res.append(copy.deepcopy(puzzle))
    solve()
    return res


def sudoku2(puzzle):
    # return the first solution found
    def solve():
        for y in range(9):
            for x in range(9):
                if puzzle[y][x] == 0:
                    for n in range(1, 10):
                        if possible(y, x, n, puzzle):
                            puzzle[y][x] = n
                            if solve():
                                return puzzle
                            puzzle[y][x] = 0
                    return
        return True
    return solve()



if __name__ == "__main__":
    print('all solutions: \n', sudoku1(puzzle))
    print()
    print('first solution: \n', sudoku2(puzzle))