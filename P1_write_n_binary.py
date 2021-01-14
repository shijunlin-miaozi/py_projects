# This program writes all possible binary strings of length n into a text file, one string in one line

# approach:
    # start with all "0"s, then replace "0"s with "1"s in a systematic way to find all possibilities
    # num of "1"s in a binary stringe can range from 0(no "1" at all) to n (all "1"s)
    # for k num of "1"s in the string, use in-built function to find all conbinations (i.e. n choose k)

from itertools import combinations

def replace_chr(s, i, c = "1"):
    # replace letter at index i of a string with "1" (default)
    if i >= len(s):
        return False
    return s[:i] + c + s[i+1 :]


def write_binary_str(n, comb):
    # replace letter(s) at 1 or more index(es) of a string (default is "0"s, replace "0" with "1" at specified indexes)
    # numbers of indexes are input as tuple (e.g. (0, 2, 3) means replace letters at index 0, 2 and 3)
    s = "0" * n 
    for i in comb:
        s = replace_chr(s, i)
    return s


def binary_list(n):
    # return all possible binary strings with length n in a list
    lt, tp = [], [x for x in range(n)]
    for i in range(n + 1):
        # possible num of "1"s in a n-len binary string is 0 to n (there can be zero "1" up to n "1"s)
        comb = list(combinations(tp, i))
        for j in comb:
            lt.append(write_binary_str(n, j))
    return lt


def write_txt_file(n):
    # write all possible binary strings with length n into a txt file, line by line
    with open("binary_" + str(n) + ".txt", "w") as f:
        for el in binary_list(n):
            f.write(el + "\n")


if __name__ == '__main__':
    write_txt_file(12)

