# >>>>>>>>>>>>>>>>>>>>>>>> WORK IN PROGRESS >>>>>>>>>>>>>>>>>>>>>>>>>>
# s= [[0, 0, 0,   0, 0, 0,   0, 0, 7], 
#     [6, 0, 0,   4, 2, 0,   0, 0, 0],
#     [0, 0, 4,   9, 0, 1,   0, 0, 3],

#     [0, 0, 0,   0, 0, 9,   7, 0, 0],
#     [0, 0, 6,   0, 0, 8,   4, 0, 0],
#     [8, 9, 1,   0, 0, 4,   0, 0, 0],

#     [0, 0, 9,   0, 5, 6,   0, 1, 0],
#     [0, 0, 0,   0, 0, 0,   0, 0, 8],
#     [5, 0, 0,   0, 0, 0,   0, 0, 0]] # solved

s= [[4, 0, 0,   0, 0, 0,   0, 7, 8], 
    [7, 0, 0,   1, 0, 0,   4, 0, 9],
    [0, 0, 2,   3, 0, 0,   0, 0, 0],

    [1, 0, 0,   4, 0, 6,   0, 0, 0],
    [0, 6, 0,   0, 0, 0,   0, 0, 0],
    [0, 4, 0,   0, 5, 3,   1, 0, 0],

    [0, 0, 0,   5, 0, 0,   0, 0, 0],
    [8, 1, 3,   0, 0, 0,   0, 0, 7],
    [0, 0, 0,   0, 2, 0,   0, 0, 0]] # unsolved

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
    if has_update(d): 
        print('has update fr calc cstr')
    return d

def update_sudoku_dict(d, ref):
    update = {}
    for label, cstr in d['blank'].items():
        if len(cstr) == 1:
            update.setdefault(label, list(cstr)[0])
    print('blanks filled:   ', len(update))
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

def make_cstr_dict(d):
    cstr_d = {}
    for label in d['blank']:
        for i in label:
            cstr_d[i] = cstr_d.setdefault(i, set()) | {label}
    return cstr_d

def sole_poss(d):
    ctr = 0
    cstr_d = make_cstr_dict(d)
    for j in cstr_d:
        for label in cstr_d[j]:
            n = union_n_diff(d, cstr_d[j], cstr_d[j] - {label})
            if len(n) == 1 and len(d['blank'][label]) != 1:
                ctr += 1
                d['blank'][label] = n
                print('....................sole_poss')
    print('total sole_poss: ', ctr, 'times')
    return d

def direct_solve(d, ref):
    ctr = 0
    while has_update(d):
        d = update_sudoku_dict(d, ref)
        d = calc_constraint(d)
        d = sole_poss(d)
        ctr += 1
    print('----------------direct solve iteration: ', ctr, '     total:', len(d['blank']) + len(d['ans']), '      solved:', len(d['ans']), '      UNSOLVED:', len(d['blank']))
    return d

def eliminate(to_remove, remove_from, d): # 1st para is cstr set to be eliminated, 2nd is label set from which cstr is eliminated, 3rd is sudoku dict
    ctr = 0
    for el in to_remove:
        for label in remove_from:
            if el in d['blank'][label]:
                d['blank'][label].remove(el)
                ctr = 1
    return ctr, d

def union_n_diff(d, label_set1, label_set2=set()): # 1st para is sudoku dict, 2nd & 2rd para are label sets, return diff in cstr union of the 2 label sets
    cstr1, cstr2 = set(), set()
    for x, y in zip((label_set1, label_set2), (cstr1, cstr2)):
        for label in x:
            y |= d['blank'][label]
    return cstr1 - cstr2

def indirect_solve(d):
    cstr_d = make_cstr_dict(d)
    ctr = 1
    while ctr > 0:
        ctr = 0
        for i in range(1, 10): # deduction - locked candidate
            box_d, b_num = {}, 'b' + str(i)
            if b_num not in cstr_d: continue
            for label in cstr_d[b_num]:
                for pos in range(2):
                    box_d[label[pos]] = box_d.setdefault(label[pos], []) + [label]
            for line in box_d:
                all_l, l_b = set(cstr_d[line]), set(box_d[line])
                other_l, other_b = all_l - l_b, set(cstr_d[b_num]) - l_b
                n, d = eliminate(union_n_diff(d, all_l, other_l), other_b, d)
                if n == 1: print('....has locked candidate')
                ctr += n
                if has_update(d): 
                    return d
        for j in cstr_d:
            for a, b in list(combinations(cstr_d[j], 2)):
                x, y = d['blank'][a], d['blank'][b]
                intxn = x & y
                if len(intxn) == 2:
                    if len(x) == len(y) == 2: # deduction - naked pair
                        n, d = eliminate(intxn, cstr_d[j] - {a, b}, d)
                        if n == 1: print('........has naked pair')
                        ctr += n
                        if has_update(d): 
                            return d
                    other = union_n_diff(d, cstr_d[j] - {a, b}) 
                    if len(intxn & other) == 0 and (len(x) > 2 or len(y) > 2): # deduction - hidden pair
                        for to, fr in zip((x - intxn, y - intxn), ({a}, {b})):
                            n, d = eliminate(to, fr, d)
                            if n == 1: print('............has hidden pair')
                            ctr += n
                        if has_update(d): 
                            return d
            for a, b, c in list(combinations(cstr_d[j], 3)):
                x, y, z = d['blank'][a], d['blank'][b], d['blank'][c]
                uni = x | y | z
                if len(uni) == 3: # deduction - naked triplet
                    n, d = eliminate(uni, cstr_d[j] - {a, b, c}, d)
                    if n == 1: print('................has naked triplet')
                    ctr += n
                    if has_update(d): 
                        return d
                diff = union_n_diff(d, cstr_d[j], cstr_d[j] - {a, b, c})
                if len(diff) == 3: # deduction = hidden triplet
                    for to, fr in zip((x - diff, y - diff, z - diff), ({a}, {b}, {c})):
                        n, d = eliminate(to, fr, d)
                        if n == 1: print('....................has hidden triplet')
                        ctr += n
                        if has_update(d): 
                            return d
        d = sole_poss(d)
        if has_update(d): 
            return d 
        pair_d = {}
        for i in range(1, 10):
            pair_d.setdefault(i, {'r': {}, 'c': {}})
        for j in cstr_d:
            if j[0] == 'b': continue
            for a, b in list(combinations(cstr_d[j], 2)):
                n = union_n_diff(d, cstr_d[j], cstr_d[j] - {a, b})
                if len(n) == 1:
                    [a, b], r_d, c_d = sorted([a, b]), pair_d[list(n)[0]]['r'], pair_d[list(n)[0]]['c']
                    if a[0] == b[0]:
                        r_d[(a[1][1], b[1][1])] = r_d.setdefault((a[1][1], b[1][1]), []) + [(a, b)]
                    else:
                        c_d[(a[0][1], b[0][1])] = c_d.setdefault((a[0][1], b[0][1]), []) + [(a, b)]
        for num, val1 in pair_d.items():
            for r_c, val2 in val1.items():
                for pos, pair in val2.items():
                    if len(pair) == 2: # deduction - x-wing
                        line = list({'r', 'c'} - set(r_c))[0]
                        remove_fr = (cstr_d[line + pos[0]] | cstr_d[line + pos[1]]) - (set(pair[0]) | set(pair[1]))
                        n, d = eliminate(set([num]), remove_fr, d)
                        if n == 1: print('....................has x-wing')
                        ctr += n
                        if has_update(d): 
                            return d
                    elif len(val2) > 2:
                        for a, b, c in list(combinations(list(val2.keys()), 3)):
                            uni = list(set(a) | set(b) | set(c))
                            if len(uni) == 3: # deduction - swordfish
                                line = list({'r', 'c'} - set(r_c))[0]
                                all_blank, multi_pair, k = set(), set(), (a, b, c)
                                for i, k in zip((0, 1, 2), (a, b, c)):
                                    all_blank |= cstr_d[line + uni[i]]
                                    multi_pair |= {val2[k][0][0], val2[k][0][1]}
                                # print('val2 is:\n', val2)
                                # print(len(all_blank))
                                # print(len(multi_pair))
                                # print(a, b, c)
                                # print(multi_pair)
                                # print(len(all_blank - multi_pair))
                                n, d = eliminate(set([num]), all_blank - multi_pair, d)
                                print(n)
                                if n == 1: print('........................has swordfish')
                                ctr += n
                                if has_update(d): 
                                    return d
        # label_set = set()
        # for label, cstr in d['blank'].items():
        #     if len(cstr) == 2:
        #         label_set.add(label)
        # for x, y, z in list(combinations(label_set, 3)):
        #     if x[0] == y[0] == z[0] or x[1] == y[1] == z[1] or x[2] == y[2] == z[2]: continue
        #     if len(union_n_diff(d, {x, y, z})) == 3 and d['blank'][x] != d['blank'][y] != d['blank'][z] != d['blank'][x]:
        #         if x[2] != y[2] != z[2] != x[2]: # deduction - xy-wing (w right angle)
        #             print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> k is: ', x, y, z)
        #             for i in [x, y, z]:
        #                 print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> cstr is: ', d['blank'][i])



# * change done: add sole_poss func as part of direct solve; corrected x-wing and swordfish code; shorten code re combi func          
# TODO: add 2 more rules: xy-wing, xy-wing(w right angle); run test on large sudoku sample to find optimal rule sequence if any; add code to guess if none of the rules apply
# ? with given rules, some paths result in solution while others not, to rerun the code multiple times if first round doesn't result in solution? or start guessing right away? run efficiency test 

def sudoku_solver(s, ref):
    d = make_sudoku_dict(s, ref['make_dict'])
    d = calc_constraint(d)
    d = sole_poss(d)
    d = direct_solve(d, ref['update_dict'])
    ctr = 0
    while not has_answer(d):
        d = indirect_solve(d)
        ctr += 1
        d = direct_solve(d, ref['update_dict'])
    print('-----------------------------------deduction iteration:', ctr, '\n\n', 'Final Answer is:')
    return write_answer(s, d)

if __name__ == '__main__':
    pass

    import time
    start_time = time.time()
    ref = ref_table()
    ans = sudoku_solver(s, ref)
    print(ans)
    print('--- runtime: %.3fs seconds ---' % (time.time() - start_time))

# >>>>>>>>>>>>>>>>>>>>>>>> WORK IN PROGRESS >>>>>>>>>>>>>>>>>>>>>>>>>>