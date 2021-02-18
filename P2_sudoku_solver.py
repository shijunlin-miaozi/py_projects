# >>>>>>>>>>>>>>>>>>>>>>>> WORK IN PROGRESS >>>>>>>>>>>>>>>>>>>>>>>>>>
s= [[3, 0, 0,   0, 0, 0,   0, 2, 0], 
    [1, 0, 2,   7, 0, 0,   8, 0, 4],
    [0, 5, 0,   0, 3, 0,   0, 0, 0],

    [0, 0, 0,   0, 8, 0,   0, 0, 0],
    [0, 0, 0,   0, 0, 7,   0, 0, 1],
    [0, 7, 4,   9, 6, 0,   0, 0, 3],

    [7, 0, 0,   0, 0, 3,   0, 0, 0],
    [0, 2, 0,   0, 0, 0,   0, 1, 0],
    [0, 0, 9,   8, 5, 0,   0, 0, 0]] # solved with 14 guess

from itertools import combinations
import copy, csv

def ref_table():
    d = {'row_index_to_label': {}, 'label_to_index_map': {}}
    for row in range(9):
        base = '012'* 3 if row in (0, 3, 6) else '345'* 3 if row in (1, 4, 7) else '678'* 3
        for index in range(9):
            b = (1, 2, 3) if row < 3 else (7, 8, 9) if row > 5 else (4, 5, 6)
            b = b[0] if index < 3 else b[2] if index > 5 else b[1]
            label = 'r' + str(row + 1), 'c' + str(index + 1), 'b' + str(b)
            mapping = index, row, int(base[index])
            d['row_index_to_label'].setdefault((row, index), label)
            d['label_to_index_map'].setdefault(label, mapping)
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
    for label in d['blank']:
        cstr = set(j for i in label for j in d[i] if j != 0)
        d['blank'][label] = {1, 2, 3, 4, 5, 6, 7, 8, 9} - cstr
    return d

def update_sudoku_dict(d, ref):
    update = {}
    for label, cstr in d['blank'].items():
        if len(cstr) == 1:
            update.setdefault(label, *cstr)
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
    for i in d:
        if i != 'blank' and i != 'ans' and sorted(d[i]) != [1, 2, 3, 4, 5, 6, 7, 8, 9]: 
            return False
    return True

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
    
def eliminate(to_remove, remove_from, d): # 1st para is cstr set to be eliminated, 2nd is label set from which cstr is eliminated
    ctr = 0
    for el in to_remove:
        for label in remove_from:
            if el in d['blank'][label]:
                d['blank'][label].remove(el)
                ctr = 1
    return ctr, d

def union_n_diff(d, label_set1, label_set2=set()): # 2nd & 2rd para are label sets, return diff in cstr union of the 2 label sets
    cstr1, cstr2 = set(), set()
    for x, y in zip((label_set1, label_set2), (cstr1, cstr2)):
        for label in x:
            y |= d['blank'][label]
    return cstr1 - cstr2

def sole_poss(d): # confirm a blank when it contains a cstr num that does not appear in other blanks in a row, column or box
    ctr = 1
    cstr_d = make_cstr_dict(d)
    for j in cstr_d:
        for label in cstr_d[j]:
            n = union_n_diff(d, cstr_d[j], cstr_d[j] - {label})
            if len(n) == 1 and len(d['blank'][label]) != 1:
                d['blank'][label] = n
                ctr += 1
    print('....................total sole_poss iter:', ctr)
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

def indirect_solve(d, ref): # overview of all rules http://www.pennydellsudokusolver.com/help/tips.html
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
                x, y, z = tuple(d['blank'][i] for i in [a, b, c] )
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
        if has_update(sole_poss(d)): 
            return d
        # pair_d = {}
        # for i in range(1, 10):
        #     pair_d.setdefault(i, {'r': {}, 'c': {}})
        # for j in cstr_d:
        #     if j[0] == 'b': continue
        #     for a, b in list(combinations(cstr_d[j], 2)):
        #         n = union_n_diff(d, cstr_d[j], cstr_d[j] - {a, b})
        #         if len(n) == 1 and n.issubset(d['blank'][a]) and n.issubset(d['blank'][b]):
        #             [a, b], r_d, c_d = sorted([a, b]), pair_d[list(n)[0]]['r'], pair_d[list(n)[0]]['c']
        #             if a[0] == b[0]: 
        #                 r_d[(a[1][1], b[1][1])] = r_d.setdefault((a[1][1], b[1][1]), []) + [(a, b)]
        #             else: 
        #                 c_d[(a[0][1], b[0][1])] = c_d.setdefault((a[0][1], b[0][1]), []) + [(a, b)]
        # for num, val1 in pair_d.items():
        #     for r_c, val2 in val1.items():
        #         if len(val2) > 2:
        #             for a, b, c in list(combinations(val2.keys(), 3)):
        #                 uni = list(set(a) | set(b) | set(c))
        #                 if len(uni) == 3: # deduction - swordfish
        #                     line, all_blank, multi_pair = list({'r', 'c'} - set(r_c))[0], set(), set()
        #                     for i, k in zip((0, 1, 2), (a, b, c)):
        #                         all_blank |= cstr_d[line + uni[i]]
        #                         multi_pair |= {val2[k][0][0], val2[k][0][1]}
        #                     n, d = eliminate(set([num]), all_blank - multi_pair, d)
        #                     if n == 1: print('........................has swordfish')
        #                     ctr += n
        #                     if has_update(d): 
        #                         return d
        #         for pos, pair in val2.items():
        #             if len(pair) == 2: # deduction - x-wing
        #                 line = list({'r', 'c'} - set(r_c))[0]
        #                 remove_fr = (cstr_d[line + pos[0]] | cstr_d[line + pos[1]]) - (set(pair[0]) | set(pair[1]))
        #                 n, d = eliminate(set([num]), remove_fr, d)
        #                 if n == 1: print('....................has x-wing')
        #                 ctr += n
        #                 if has_update(d): 
        #                     return d
        # label_set = set(label for label, cstr in d['blank'].items() if len(cstr) == 2) 
        # for x, y, z in list(combinations(label_set, 3)): 
        #     if x[0] == y[0] == z[0] or x[1] == y[1] == z[1] or x[2] == y[2] == z[2]: continue
        #     if len(union_n_diff(d, {x, y, z})) == 3 and d['blank'][x] != d['blank'][y] != d['blank'][z] != d['blank'][x]:
        #         seen, lt = set(), [k[i] for k in [x, y, z] for i in range(3)]
        #         dups = set(x for x in lt if x in seen or seen.add(x))
        #         if len(dups) > 1: # deduction - xy-wing
        #             if 'b' not in str(dups):
        #                 A = [k for k in [x, y, z] if dups.issubset(set(k))][0]
        #                 (B, C) = tuple({x, y, z} - {A})
        #                 label1, label2 = ref[int(C[0][1]) - 1, int(B[1][1]) - 1], ref[int(B[0][1]) - 1, int(C[1][1]) - 1]
        #                 remove_fr = [x for x in [label1, label2] if x in d['blank'] and x != A]
        #                 n, d = eliminate(union_n_diff(d, {B}, {A}), remove_fr, d)
        #                 if n == 1: print('............................has xy-wing (in 3 boxes)')
        #                 ctr += n
        #                 if has_update(d): 
        #                     return d
        #             else:
        #                 b_pair = 'b' + str(dups)[str(dups).index('b') + 1]
        #                 C = [k for k in [x, y, z] if k[2] != b_pair][0]
        #                 b_other, r_c = C[2], [x for x in dups if x in C]
        #                 if len(r_c) == 1:
        #                     A = [k for k in ({x, y, z} - {C}) if r_c[0] in k][0]
        #                     B, r_c_pair = list({x, y, z} - {A, C})[0], r_c[0]
        #                     r_c_other = r_c_pair[0] + str(B)[str(B).index(r_c_pair[0]) + 1]
        #                     remove_fr = ((cstr_d[b_pair] & cstr_d[r_c_pair]) - {A}) | (cstr_d[b_other] & cstr_d[r_c_other])
        #                     n, d = eliminate(union_n_diff(d, {B}, {A}), remove_fr, d)
        #                     if n == 1: print('............................has xy-wing (in 2 boxes)')
        #                     ctr += n
        #                     if has_update(d): 
        #                         return d
    return None, d

def rule_only_solve(d, ref):
    ctr = 0
    while not (d['blank'] == {} and final_check(d)):
        d = indirect_solve(d, ref['row_index_to_label'])
        if isinstance(d, tuple):
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> rule only solve exhaused, go to guess >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            return d[1]
        d = direct_solve(d, ref['label_to_index_map'])
        ctr += 1
    print('-----------------------------------deduction iteration:', ctr)
    return write_answer(s, d)

def sudoku_solver(s, ref):
    d = make_sudoku_dict(s, ref['row_index_to_label'])
    d = calc_constraint(d)
    d = direct_solve(d, ref['label_to_index_map'])
    d = rule_only_solve(d, ref)
    if isinstance(d, list):
        return d
    lt = sorted([[len(cstr), list(cstr), label] for label, cstr in d['blank'].items()])
    ctr = 0
    for el in lt: # guess one blank at one time
        for cstr in el[1]:
            d1 = copy.deepcopy(d)
            d1['blank'][el[2]] = {cstr}
            print('label: ', el[2], '   cstr guess: ', {cstr})
            ctr += 1
            d1 = rule_only_solve(d1, ref)
            if isinstance(d1, list):
                print('guess iteration is: ', ctr)
                return d1
            else: continue
    # i, guess = 0, [[]] # guess multiple blanks at same time
    # while i < len(lt):
    #     guess = [y + [x] for x in lt[i][1] for y in guess]
    #     for combi in guess:
    #         print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> combi is: ', combi)
    #         d1 = copy.deepcopy(d)
    #         ctr += 1
    #         print('ctr is: ', ctr)
    #         for index, cstr in zip(range(i + 1), combi):
    #             d1['blank'][lt[index][2]] = {cstr}
    #             d1 = rule_only_solve(d1, ref)
    #             if isinstance(d1, list):
    #                 print('guess iteration is: ', ctr)
    #                 return d1
    #             else: continue
    #     i += 1
    

# * change done: added guess code
# ? guess one blank at one time or multiple ones at one time? 
# ? remove complex rules (swordfish, x-wing, xy-wing) to improve efficiency? heavy code but rarely used, time wasted in checking
# TODO: run test on large sample

if __name__ == '__main__':

    # s = '004300209005009001070060043006002087190007400050083000600000105003508690042910300'
    # s2 = '040100050107003960520008000000000017000906800803050620090060543600080700250097100'
    # s3 = '600120384008459072000006005000264030070080006940003000310000050089700000502000190'

    # s4 = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'

    # sudoku = [list(map(int, s4[i : (i + 9)])) for i in range(9)]
    # print(sudoku)


    # lt = [line[0] for line in csv.reader(open('sudoku.csv'))]
    # print(s_lt[:1])



    import time
    start_time = time.time()
    ref = ref_table()
    ans = sudoku_solver(s, ref)
    print(ans)
    # print('--- runtime: %.2fs seconds ---' % (time.time() - start_time))
    print(f'--- runtime: {(time.time() - start_time): .2f} s seconds ---')

# >>>>>>>>>>>>>>>>>>>>>>>> WORK IN PROGRESS >>>>>>>>>>>>>>>>>>>>>>>>>>
