'''doc?'''
# import sys
import re
import numpy as np

class Board:
    '''docstring'''
    trans = [' ', 'X', 'O']
    def __init__(self):
        # self.brd = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
        self.brd = np.zeros((3, 3))

    def print_board(self):
        '''prints the board'''
        for i in range(3):
            # for j in range(3):
            #     if i < 2:
            print(Board.trans[int(self.brd[i, 0])], '|',
                Board.trans[int(self.brd[i, 1])],
                '|', Board.trans[int(self.brd[i, 2])])
            if i < 2:
                print(9 * "-")

    def add_x(self, row, col):
        '''attempts to put an X at the specified location on the board'''
        # if self.brd[row][col] != ' ':
        if self.brd[row, col] != 0:
            print ("Can't put an X there!")
            return -1
        else:
            # self.brd[row][col] = 'X'
            self.brd[row, col] = 1
            return 0

    def add_o(self, row, col):
        '''attempts to put an O at the specified location on the board'''
        # if self.brd[row][col] != ' ':
        if self.brd[row, col] != 0:
            print ("Can't put an O there!")
            return -1
        else:
            # self.brd[row][col] = 'O'
            self.brd[row, col] = 2
            return 0

    def win_condition(self):
        '''returns 0 if no one's won, 1 if X has won, and 2 if O has won'''
        # lists = []
        for i in range(3):
            xwin = [1, 1, 1]
            owin = [2, 2, 2]
            hor_slice = np.ndarray.tolist(self.brd[i, :])
            ver_slice = np.ndarray.tolist(self.brd[:, i])
            for i in range(3):
                hor_slice[i] = int(hor_slice[i])
                ver_slice[i] = int(ver_slice[i])
            cross_slice_1 = [self.brd[0, 0], self.brd[1, 1], self.brd[2, 2]]
            cross_slice_2 = [self.brd[0, -1], self.brd[1, -2], self.brd[2, -3]]
            if hor_slice == xwin or ver_slice == xwin or cross_slice_1 == xwin or cross_slice_2 == xwin:
                return 1
            elif hor_slice == owin or ver_slice == owin or cross_slice_1 == owin or cross_slice_2 == owin:
                return 2
            else:
                return 0
            # lists += [hor_slice]
            # lists += [ver_slice]

'''GAME LOOP'''
board = Board()

def print_help():
    '''prints help'''
    h = '''Just like normal tic-tac-toe rules. Input should be two numbers in\n
    [1..3] separated by a single space. The first number should be row\n
    (top-to-bottom) and the second number should be column (left-to-right).\n
    Enter 'quit' or 'exit' to leave.'''
    print(h)

def collapse_whitespace(s):
    '''collapses adjacent spaces into one space'''
    if '  ' in s:
        return collapse_whitespace(s.replace('  ', ' '))
    return s

def get_move(st):
    s = collapse_whitespace(st)
    intlst = s.split()
    for i in range(2):
        intlst[i] = int(intlst[i]) - 1
    return intlst[0], intlst[1]

def move(s, brd, turn): # turn is 1 if X and 2 if O
    m, n = get_move(s)
    if turn == 1:
        ex = brd.add_x(m, n)
    elif turn == 2:
        ex = brd.add_o(m, n)
    else:
        print("can't get here")
        return -1
    return ex

for i in range(9):
    board.print_board()
    ex_code = (-10000) # update this with method exit codes - nest a while loop that runs until it exits with 0
    while ex_code < 0:
        inp = input().strip()
        if inp.lower() == 'quit' or inp.lower() == 'exit':
            ex_code = 3
            break
        elif re.fullmatch(r'[1-3] +[1-3]', inp):
            ex_code = move(inp, board, (i % 2) + 1)
        else:
            print('Bad input. Try again!')
    if ex_code == 3:
        break
    if board.win_condition() > 0:
        board.print_board()
        winner = 'X' if board.win_condition() == 1 else 'O'
        print(winner, 'wins!')
        break
    if i == 9:
        board.print_board()
        print("It's a draw, folks!")
