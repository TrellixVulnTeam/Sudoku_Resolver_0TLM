import copy
import math
import random
import itertools
from math import trunc
from timeit import Timer
from random import sample


def LoadRandomSolvedSudoku():
    f = open("SolvedSudoku.txt", "r")
    for i in range(1, random.randint(0, 9999)):
        f.readline()
    sudokuLine = f.readline()
    sudoku = []
    for i in range(0, 9):
        sudoku.append(list(map(int, sudokuLine[9 * i:9 * (i + 1)])))
    return sudoku


def CreateRandomSolvedSudoku():
    rows = [g * 3 + r for g in sample(range(3), 3) for r in sample(range(3), 3)]
    cols = [g * 3 + c for g in sample(range(3), 3) for c in sample(range(3), 3)]
    nums = sample(range(1, 10), 9)
    return [[nums[(3 * (r % 3) + r // 3 + c) % 9] for c in cols] for r in rows]


def CreateSudoku(solvedSudoku):
    nCells = random.randint(15, 25)
    for i in range(1, 81 - nCells):
        solvedSudoku[random.randint(0, 8)][random.randint(0, 8)] = 0
    return solvedSudoku


def ArcConsistency(puzzle):
    queue = copy.deepcopy(puzzle.costraints)
    while queue:
        index = queue.pop(0)
        if Revise(index, puzzle):
            if not puzzle.domains[index[0][0]][index[0][1]]:
                return False
            newarcs = [[[index[0][0], index[0][1]], [index[0][0], k]] for k in range(0, 9)]
            newarcs += [[[index[0][0], index[0][1]], [k, index[0][1]]] for k in range(0, 9)]
            x = index[0][0] - index[0][0] % 3
            y = index[0][1] - index[0][1] % 3
            newarcs += [[[index[0][0], index[0][1]], [k, l]] for k, l in
                        itertools.product(range(x, x + 3), range(y, y + 3))]
            newarcs.sort()
            newarcs = list(newarcs for newarcs, _ in itertools.groupby(newarcs))
            for i, j in itertools.product(range(0, 9), range(0, 9)):
                if [[i, j], [i, j]] in newarcs: newarcs.remove([[i, j], [i, j]])
            newarcs.remove([[index[0][0], index[0][1]], [index[1][0], index[1][1]]])
            queue += newarcs
    return True


def Revise(index, puzzle):
    revised = False
    if index[1] != index[0]:
        for x in puzzle.domains[index[0][0]][index[0][1]]:
            if x == puzzle.variables[index[1][0]][index[1][1]]:
                puzzle.domains[index[0][0]][index[0][1]].remove(x)
                revised = True
    return revised


def fowardChaining(puzzle, var):
    puzzle.domains[var[0]][var[1]] = [puzzle.variables[var[0]][var[1]]]
    for i in range(0, 9):
        Revise([[var[0], i], [var[0], var[1]]], puzzle)
        Revise([[i, var[1]], [var[0], var[1]]], puzzle)
        if not puzzle.domains[i][var[1]] or not puzzle.domains[var[0]][i]:
            global nbackTrack
            nbackTrack += 1
            return False
    x = var[0] - var[0] % 3
    y = var[1] - var[1] % 3
    for i, j in itertools.product(range(x, x + 3), range(y, y + 3)):
        Revise([[i, j], [var[0], var[1]]], puzzle)
        if not puzzle.domains[i][j]:
            return False
    return True


def MAC(puzzle, var):
    queue = [[[var[0], i], [var[0], var[1]]] for i in range(0, 9)]
    queue += [[[i, var[1]], [var[0], var[1]]] for i in range(0, 9)]
    x = var[0] - var[0] % 3
    y = var[1] - var[1] % 3
    queue += [[[i, j], [var[0], var[1]]] for i, j in itertools.product(range(x, x + 3), range(y, y + 3))]
    for i, j in itertools.product(range(0, 9), range(0, 9)):
        if [[i, j], [i, j]] in queue: queue.remove([[i, j], [i, j]])
    while queue:
        index = queue.pop(0)
        if Revise(index, puzzle):
            if not puzzle.domains[index[0][0]][index[0][1]]:
                global nbackTrack
                nbackTrack += 1
                return False
            newarcs = [[[index[0][0], index[0][1]], [index[0][0], k]] for k in range(0, 9)]
            newarcs += [[[index[0][0], index[0][1]], [k, index[0][1]]] for k in range(0, 9)]
            x = index[0][0] - index[0][0] % 3
            y = index[0][1] - index[0][1] % 3
            newarcs += [[[index[0][0], index[0][1]], [k, l]] for k, l in
                        itertools.product(range(x, x + 3), range(y, y + 3))]
            newarcs.sort()
            newarcs = list(newarcs for newarcs, _ in itertools.groupby(newarcs))
            for i, j in itertools.product(range(0, 9), range(0, 9)):
                if [[i, j], [i, j]] in newarcs: newarcs.remove([[i, j], [i, j]])
            newarcs.remove([[index[0][0], index[0][1]], [index[1][0], index[1][1]]])
            queue += newarcs
    return True


class Sudoku:
    def __init__(self, puzzle):
        self.variables = puzzle
        self.costraints = self.createCostraints()
        self.domains = self.createDomains()

    def isComplete(self):
        for i, j in itertools.product(range(0, 9), range(0, 9)):
            if self.variables[i][j] == 0:
                return False
        return True

    def createCostraints(self):
        costraints = []
        costraints += [[[i, j], [i, k]] for i, j, k in itertools.product(range(0, 9), range(0, 9), range(0, 9))]
        costraints += [[[i, j], [k, j]] for i, j, k in itertools.product(range(0, 9), range(0, 9), range(0, 9))]
        for x, y in itertools.product(range(0, 9, 3), range(0, 9, 3)):
            costraints += [[[i, j], [k, l]] for i, j, k, l in
                           itertools.product(range(x, x + 3), range(y, y + 3), range(x, x + 3), range(y, y + 3))]
        costraints.sort()
        costraints = list(costraints for costraints, _ in itertools.groupby(costraints))
        for i, j in itertools.product(range(0, 9), range(0, 9)):
            if [[i, j], [i, j]] in costraints: costraints.remove([[i, j], [i, j]])
        return costraints

    def createDomains(self):
        domains = [[[1, 2, 3, 4, 5, 6, 7, 8, 9] for _ in range(0, 9)] for _ in range(0, 9)]
        for i, j in itertools.product(range(0, 9), range(0, 9)):
            if self.variables[i][j] != 0:
                domains[i][j] = [self.variables[i][j]]
        return domains

    def getVariable(self):
        domainDimension = [len(self.domains[i][j]) if self.variables[i][j] == 0 else math.inf for i, j in
                           itertools.product(range(0, 9), range(0, 9))]
        vars = [i for i, x in enumerate(domainDimension) if x == min(domainDimension)]
        return [trunc(vars[0] / 9), vars[0] % 9]

    def isConsistent(self, var, val):
        for i in range(0, 9):
            if self.variables[var[0]][i] == val:
                return False
            if self.variables[i][var[1]] == val:
                return False
        x = var[0] - var[0] % 3
        y = var[1] - var[1] % 3
        for i, j in itertools.product(range(x, x + 3), range(y, y + 3)):
            if self.variables[i][j] == val:
                return False
        return True

    def getOrder(self, var):
        rating = [0 for _ in range(0, 10)]
        for i in range(0, 9):
            for k in self.domains[var[0]][i]:
                rating[k] += 1
            for k in self.domains[i][var[1]]:
                rating[k] += 1
        x = var[0] - var[0] % 3
        y = var[1] - var[1] % 3
        for i, j in itertools.product(range(x, x + 3), range(y, y + 3)):
            for k in self.domains[i][j]:
                rating[k] += 1
        finalOrder = []
        for i in self.domains[var[0]][var[1]]:
            finalOrder.append(rating[i])
        zipped_lists = zip(finalOrder, self.domains[var[0]][var[1]])
        sorted_zipped_lists = sorted(zipped_lists, reverse=True)
        zipped_lists = [element for _, element in sorted_zipped_lists]
        return zipped_lists


def backTrackingSudokuMAC(sudoku):
    if sudoku.isComplete(): return sudoku
    var = sudoku.getVariable()
    for val in sudoku.getOrder(var):
        if sudoku.isConsistent(var, val):
            sudoku.variables[var[0]][var[1]] = val
            domainBacktrack = copy.deepcopy(sudoku.domains)
            if MAC(sudoku, var):
                result = backTrackingSudokuMAC(sudoku)
                if result:
                    return result
            sudoku.domains = domainBacktrack
        sudoku.variables[var[0]][var[1]] = 0
    return False


def backTrackingSudokuFwdChaining(sudoku):
    if sudoku.isComplete(): return sudoku
    var = sudoku.getVariable()
    for val in sudoku.getOrder(var):
        if sudoku.isConsistent(var, val):
            sudoku.variables[var[0]][var[1]] = val
            domainBacktrack = copy.deepcopy(sudoku.domains)
            if fowardChaining(sudoku, var):
                result = backTrackingSudokuFwdChaining(sudoku)
                if result:
                    return result
            sudoku.domains = domainBacktrack
        sudoku.variables[var[0]][var[1]] = 0

    return False


a = [[0, 0, 5, 2, 3, 0, 0, 6, 0], [8, 2, 9, 6, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 8, 0, 0, 0, 0, 0, 2],
     [0, 0, 0, 7, 0, 9, 0, 0, 0], [3, 0, 0, 0, 0, 0, 4, 9, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [5, 0, 0, 0, 0, 4, 1, 3, 7],
     [0, 6, 0, 0, 7, 5, 9, 0, 0]]
b = [[1, 4, 6, 3, 7, 2, 5, 8, 9], [3, 2, 7, 8, 5, 9, 6, 1, 4], [8, 9, 5, 1, 6, 4, 7, 3, 2], [4, 5, 8, 2, 1, 6, 3, 9, 7],
     [9, 7, 3, 4, 8, 5, 1, 2, 6], [2, 6, 1, 9, 3, 7, 8, 4, 5], [7, 1, 2, 5, 9, 3, 4, 6, 8], [6, 8, 4, 7, 2, 1, 9, 5, 3],
     [5, 3, 9, 6, 4, 8, 2, 7, 1]]

s = Sudoku(a)
'''
s = Sudoku(CreateSudoku(LoadRandomSolvedSudoku()))

s = Sudoku(CreateSudoku(CreateRandomSolvedSudoku()))
'''
s1 = copy.deepcopy(s)
nbackTrack = 0
t = Timer(lambda: backTrackingSudokuMAC(s))
print(t.timeit(number=1))
print(nbackTrack)

nbackTrack = 0
t = Timer(lambda: backTrackingSudokuFwdChaining(s1))
print(t.timeit(number=1))
print(nbackTrack)

