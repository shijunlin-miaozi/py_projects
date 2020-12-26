# >>>>>>>>>>>>>>>>>>>>>>>> WORK IN PROGRESS >>>>>>>>>>>>>>>>>>>>>>>>>>
s= [[0, 0, 6,   0, 0, 7,   0, 0, 0], 
    [0, 0, 0,   9, 0, 0,   0, 0, 5],
    [0, 5, 0,   0, 2, 0,   1, 0, 0],

    [0, 0, 0,   0, 0, 0,   5, 6, 0],
    [0, 8, 0,   0, 7, 3,   0, 0, 0],
    [9, 0, 0,   1, 0, 0,   0, 0, 0],

    [8, 0, 0,   0, 0, 0,   0, 1, 3],
    [0, 0, 9,   0, 8, 0,   0, 0, 7],
    [5, 3, 0,   0, 0, 0,   0, 0, 4]]

from itertools import combinations

def ref_table():
    d = {'make_dict': {}, 'update_dict': {}}
    for row in range(9):
        if row in (0, 3, 6): base = '012'* 3
        elif row in (1, 4, 7): base = '345'* 3
        else: base = '678'* 3
        for index in range(9):
            if row < 3: b = (1, 2, 3)
            elif row > 5: b = (7, 8, 9)
            else: b = (4, 5, 6)
            if index < 3: b = b[0]
            elif index > 5: b = b[2]
            else: b = b[1]
            label = 'r' + str(row + 1), 'c' + str(index + 1), 'b' + str(b)
            mapping = index, row, int(base[index])
            d['make_dict'].setdefault((row, index), label)
            d['update_dict'].setdefault(label, mapping)
    return d

def make_sudoku_dict(s, ref):
    d = {'blank': {}, 'ans': {}}
    for row in range(9):
        for index in range(9):
            label = ref[row, index]
            for i in label:
                d[i] = d.setdefault(i, []) + [s[row][index]]
                if s[row][index] == 0:
                    d['blank'].setdefault(label)
    return d

def calc_constraint(d):
    base = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    for label in d['blank']:
        cstr = set()
        for i in label:
            for j in d[i]:
                if j == 0: continue
                cstr.add(j)
        d['blank'][label] = base - cstr
    return d

def update_sudoku_dict(d, ref):
    update = {}
    for label, cstr in d['blank'].items():
        if len(cstr) == 1:
            update.setdefault(label, next(iter(cstr)))
    print('blanks filled: ', len(update))
    d['ans'].update(update)
    for label in update:
        d['blank'].pop(label)
        for x, y in zip(label, ref[label]):
            d[x][y] = update[label]
    return d

def has_update(d):
    for val in d['blank'].values():
        if len(val) == 1:
            return True
    return False

def final_check(d):
    base = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for i in d:
        if i == 'blank' or i == 'ans': continue
        lt = sorted(d[i])
        if lt != base:
            return False
    return True

def has_answer(d):
    if d['blank'] == {} and final_check(d):
        return True
    return False

def write_answer(s, d):
    for label in d['ans']:
        row, index = int(label[0][1]) - 1, int(label[1][1]) - 1
        s[row][index] = d['ans'][label]
    return s

def direct_solve(d, ref):
    ctr = 0
    while has_update(d):
        d = update_sudoku_dict(d, ref)
        d = calc_constraint(d)
        ctr += 1
    print('----------------direct solve iteration: ', ctr, '     total:', len(d['blank']) + len(d['ans']), '      solved:', len(d['ans']), '      UNSOLVED:', len(d['blank']))
    return d

def make_cstr_dict(d):
    cstr_d = {}
    for label in d['blank']:
        for i in label:
            cstr_d[i] = cstr_d.setdefault(i, set()) | {label}
    return cstr_d

def indirect_solve(d):
    cstr_d = make_cstr_dict(d)
    ctr = 1
    while ctr > 0:
        ctr = 0
        for j in cstr_d:
            combi2 = list(combinations(cstr_d[j], 2))
            for k in combi2:
                x, y = d['blank'][k[0]], d['blank'][k[1]]
                intxn = x & y
                if len(intxn) == 2:
                    if len(x) == len(y) == 2: # deduction - naked pair
                        print('.......has naked pair')
                        for label in (cstr_d[j] - set(k)):
                            for e in intxn:
                                if e in d['blank'][label]:
                                    assert d['blank'][label] == set()
                                    d['blank'][label].remove(e)
                                    ctr += 1
                                    if has_update(d):
                                        return d
                    other_label, other_cstr = cstr_d[j] - set(k), set()
                    for label in other_label:
                        other_cstr |= d['blank'][label]
                    if list(intxn)[0] not in other_cstr and list(intxn)[1] not in other_cstr: # deduction - hidden pair
                        print('........has hidden pair')
                        diff = {tuple(x - intxn): k[0], tuple(y - intxn): k[1]}
                        for i in diff:
                            if len(i) != 0:
                                for t in i:
                                    d['blank'][diff[i]].remove(t)
                                    assert d['blank'][diff[i]] == set()
                                    ctr += 1
                                    if has_update(d):
                                        return d
            combi3 = list(combinations(cstr_d[j], 3))
            for k in combi3:
                x, y, z = d['blank'][k[0]], d['blank'][k[1]], d['blank'][k[2]]
                union_3 = x | y | z
                if len(union_3) == 3: # deduction - naked triplet
                    print('........has naked triplet')
                    print(x, y, z)
                    print(union_3)
                    for label in (cstr_d[j] - set(k)):
                            for e in union_3:
                                if e in d['blank'][label]:
                                    assert d['blank'][label] == set()
                                    d['blank'][label].remove(e)
                                    ctr += 1
                                    if has_update(d):
                                        return d
                other_label, other_cstr, discard = cstr_d[j] - set(k), set(), {}
                for label in other_label:
                    other_cstr |= d['blank'][label]
                all_cstr = union_3 | other_cstr
                union_diff = all_cstr - other_cstr
                if len(union_diff) == 3: # deduction = hidden triplet
                    print('........has hidden triplet')
                    for label, cstr in zip(k, (x, y, z)):
                        for e in cstr:
                            if e not in union_diff:
                                discard.setdefault(label, []) + [e]
                    for label, cstr in discard.items():
                        if len(cstr) != 0:
                            for num in cstr:
                                assert d['blank'][label] == set()
                                d['blank'][label].remove(num)
                                ctr += 1
                                if has_update(d):
                                    return d
    print(cstr_d)
    print(d['blank'])

def sudoku_solver(s, ref):
    d = make_sudoku_dict(s, ref['make_dict'])
    d = calc_constraint(d)
    d = direct_solve(d, ref['update_dict'])
    ctr = 0
    while not has_answer(d):
        d = indirect_solve(d)
        ctr += 1
        if has_update(d):
            d = direct_solve(d, ref['update_dict'])
    print('-----------------------------------deduction iteration:', ctr)
    return write_answer(s, d)

if __name__ == '__main__':
    pass
    ref = ref_table()
    ans = sudoku_solver(s, ref)
    print(ans)


# >>>>>>>>>>>>>>>>>>>>>>>> WORK IN PROGRESS >>>>>>>>>>>>>>>>>>>>>>>>>>


