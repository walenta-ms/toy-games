'''add doc'''

import re
import numpy as np
import pygame
from pygame.locals import *
import sys
import random
from abc import ABC, abstractmethod

# width, height, #mines
BEGINNER = (9, 9, 10)
INTERMEDIATE = (16, 16, 40)
EXPERT = (30, 16, 99)
BLANK =         pygame.image.load('mines/unrevealed/blank.png')
BLANK_PRESSED = pygame.image.load('mines/unrevealed/blank-pressed.png')
FLAG =          pygame.image.load('mines/unrevealed/flag.png')
QM =            pygame.image.load('mines/unrevealed/q.png')
QM_PRESSED =    pygame.image.load('mines/unrevealed/q-pressed.png')

ZERO =  pygame.image.load('mines/revealed/0.png')
ONE =   pygame.image.load('mines/revealed/1.png')
TWO =   pygame.image.load('mines/revealed/2.png')
THREE = pygame.image.load('mines/revealed/3.png')
FOUR =  pygame.image.load('mines/revealed/4.png')
FIVE =  pygame.image.load('mines/revealed/5.png')
SIX =   pygame.image.load('mines/revealed/6.png')
SEVEN = pygame.image.load('mines/revealed/7.png')
EIGHT = pygame.image.load('mines/revealed/8.png')

number_files = [ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT]

MINE =         pygame.image.load('mines/revealed/mine.png')
MINE_FALSE =   pygame.image.load('mines/revealed/mine-false.png')
MINE_PRESSED = pygame.image.load('mines/revealed/mine-pressed.png')

# revealed_safes = 0

# counts every board elmt vert/horiz/diag adjacent to (i, j) (IN SQUARE BOARD) 
# and returns for how many [lam elt] is True
# NOT FOR TRANSPOSED BOARD (takes [board])
def over_adj(i, j, board, lam):
    acc = 0
    i_size = len(board)
    j_size = len(board[0])
    for y in range(max(0, i - 1), min(i_size, i + 2)):
        for x in range(max(0, j - 1), min(j_size, j + 2)):
            if (y, x) != (i, j):
                if lam (board[y][x]):
                    acc += 1
    return acc

# clicks every board elmt vert/horiz/diag adjacent to (i, j) (IN SQUARE BOARD)
# and list of (i, j)s for which the click val is 0
# ONLY FOR TRANPOSED BOARD (takes [droab])
def click_over_adj(i, j, board):
    acc = []
    x_size = len(board.tileses)
    y_size = len(board.tileses[0])

    for x in range(max(0, i - 1), min(x_size, i + 2)):
        for y in range(max(0, j - 1), min(y_size, j + 2)):
            if (x, y) != (i, j):
                ret = board.tileses[x][y].click(1, board)
                if ret == 1:
                    acc += [(x, y)]
                elif ret == -1:
                    return ret
    return acc

def click_over_adj_rec(i, j, board):
    zeroes = click_over_adj(i, j, board)
    while zeroes:
        if zeroes == -1:
            return -1
        fst = zeroes.pop()
        zeroes += click_over_adj(fst[0], fst[1], board)


# returns an np array OR where k=[0-8] represents a safe tile w/ k adjacent
# mines and -1 represents a mine tile
def set_board(x=16, y=16, minenum=40):
    board = np.zeros((y, x), dtype=np.int8)
    if minenum > x * y:
        print("Too many mines.")
        return
    safes = [(i, j) for i in range(y) for j in range(x)]
    mines = []
    m = minenum
    while m > 0:
        mines += [safes.pop(random.randrange(len(safes) - 1))]
        m -= 1
    for mine in mines:
        board[mine[0], mine[1]] = -1
    is_mine = lambda x : x == -1
    for safe in safes:
        board[safe[0], safe[1]] = over_adj(safe[0], safe[1], board, is_mine)
    return board


# assuming all buttons are square
# MAKE THIS ABSTRACT
class Button(ABC):

    @abstractmethod
    def l_click(self):
        pass

    @abstractmethod
    def r_click(self):
        pass

    @abstractmethod
    def click(self):
        pass


class Tile(Button, ABC):
    def __init__(self, p):
        self.size = 16
        self.pos = p
        self.revealed = False # to make revealed tiles uninteractable-with
        self.img = BLANK
        self.b_pressed = BLANK_PRESSED
        self.q_pressed = QM_PRESSED

    @abstractmethod
    def reveal(self):
        pass

    @abstractmethod
    def l_click(self):
        pass

    def l_down(self):
        None

    def r_click(self):
        '''never call directly (will not check for revealed)'''
        if self.img == BLANK:
            self.img = FLAG
        elif self.img == FLAG:
            self.img = QM
        elif self.img == QM:
            self.img = BLANK
        return 0

    @abstractmethod
    def click(self):
        pass

    def draw(self, surface):
        surface.blit(self.img, self.pos)


class MineTile(Tile):

    def reveal(self):
        if self.revealed:
            return
        if self.img != FLAG:
            self.img = MINE
        self.revealed = True

    def l_click(self):
        '''never call directly (will not check for revealed)'''
        if self.img == FLAG:
            return 0
        # elif self.img == self.revealed_img:
        #     return 0
        else:
            self.img = MINE_PRESSED
            self.revealed = True
            print("GAME OVER: LOSS")
            return -1
    
    def click(self, pressed, board):
        '''note: [board] is only here so that this has the same #args as
        [SafeTile.click()]'''
        # pressed = pygame.mouse.get_pressed()
        # print(pressed)
        # print(pressed, pressed == 3)
        # print('img:', self.img)
        if self.revealed:
            return 0
        if pressed == 1:
            return self.l_click()
        elif pressed == 3:
            return self.r_click()


class SafeTile(Tile):
    def __init__(self, p, num_mines):
        super().__init__(p)
        if num_mines > 8 or num_mines < 0:
            # print(num_mines)
            print("bad #mines")
            pygame.quit()
            exit(-1)
        # print(num_mines)
        self.mine_num = num_mines
        self.revealed_img = number_files[num_mines]

    def reveal(self):
        if self.revealed:
            return
        if self.img == FLAG:
            self.img = MINE_FALSE
        # else:
        #     self.img = self.revealed_img # or just do nothing
        self.revealed = True

    def l_click(self, board):
        '''never call directly (will not check for revealed)'''
        # global revealed_safes
        if self.img == FLAG:
            return 0
        # elif self.img == self.revealed_img: # SHOULD NEVER REACH THIS
        #     return 0 # return 0 means normal safe click
        elif self.revealed_img == number_files[0]:
            self.revealed = True
            self.img = self.revealed_img
            board.revealed_safes += 1
            return 1 # return 1 means click hit an empty tiles
        else:
            self.revealed = True
            self.img = self.revealed_img
            board.revealed_safes += 1
            return 0
    
    def click(self, pressed, board):
        if self.revealed:
            return 2 # RETURN CODE 2 means they clicked a revealed tile
        if pressed == 1:
            return self.l_click(board)
        elif pressed == 3:
            return self.r_click()

# class RestartButton(Button):
#     None
    # define right-click as an empty return for this button

class Board:
    def __init__(self, x, y, ms, x_buf, y_buf):
        self.x_ax = x
        self.y_ax = y
        self.mines = ms
        self.board = set_board(x, y, ms)
        self.draob = np.transpose(self.board)
        self.revealed_safes = 0
        self.safes = 0
        self.tileses = [[] for _ in range(x)]
        for x in range(len(self.draob)):
            for y in range(len(self.draob[x])):
                if self.draob[x, y] == -1:
                    self.tileses[x] += [MineTile((16 * x + x_buf, 16 * y + y_buf))] # add mine
                else:
                    self.tileses[x] += [SafeTile((16 * x + x_buf, 16 * y + y_buf), self.draob[x, y])] # add safe
                    self.safes += 1
    
    def board_click(self, x, y, button):
        if x > -1 and y > -1 and x < self.x_ax and y < self.y_ax:
            keys_pressed = pygame.key.get_pressed()
            ctrl_click = keys_pressed[pygame.K_RCTRL] or keys_pressed[pygame.K_LCTRL]
            new_ret = 0
            if ctrl_click:
                ret = self.tileses[x][y].click(3, self)
            else:
                ret = self.tileses[x][y].click(button, self)
            if ret == 1:
                new_ret = click_over_adj_rec(x, y, self)
            if ret == 2:
                # True if #flags around SafeTile == #mines around SafeTile
                flags_mines_eq = over_adj(x, y, self.tileses, lambda t : t.img == FLAG) == self.tileses[x][y].mine_num
                if flags_mines_eq:
                    new_ret = click_over_adj_rec(x, y, self)
            if ret == -1 or new_ret == -1:
                print('yeah you lost')
                for i in range(self.x_ax):
                    for j in range(self.y_ax):
                        self.tileses[i][j].reveal()

    def is_finished(self):
        return self.revealed_safes == self.safes

    def draw(self, surf):
        for tiles in self.tileses:
            for tile in tiles:
                tile.draw(surf)

def main():
    pygame.init()
    logo = pygame.image.load("mines/moods/happy.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("basic display")

    # X_AX = 16
    # Y_AX = 16
    # TOTAL_MINES = 40

    diff = INTERMEDIATE

    X_AX = diff[0]
    Y_AX = diff[1]
    TOTAL_MINES = diff[2]

    DARK_GREY = (65, 65, 65)
    GREY = (100, 100, 100)

    X_BUF = 10
    Y_BUF = 10
    DISPLAYSURF = pygame.display.set_mode((X_AX * 16 + 2 * X_BUF, Y_AX * 16 + 2 * Y_BUF))
    DISPLAYSURF.fill(GREY)
    FPS = pygame.time.Clock()
    FPS.tick(60)
    
    board = Board(X_AX, Y_AX, TOTAL_MINES, X_BUF, Y_BUF)
    # print(board)
    # BOARD INDEX (i, j) MAPS TO TILESES INDEX (j, i) BECAUSE OTHERWISE YOU'D BE
    # INDEXING TILES BY (y, x) (I think? that might make absolutely zero sense)
    # okay transposed the board so hopefully everything is okay now
    # draob = np.transpose(board)
    # print(draob)
    

    # global revealed_safes
    # revealed_safes = 0

    # tileses = [[SafeTile((16 * i + X_BUF, 16 * j + Y_BUF), random.randint(0, 8))
    #           for j in range(16)] for i in range(16)]

    while True:
        for event in pygame.event.get():
            rel_pos = (-1, -1)
            # pressed = tuple()
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # TODO: catch MOUSEBUTTONDOWNs to display pressed (unreleased) buttons
            elif event.type == MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                rel_pos = (int((pos[0] - X_BUF) / 16), int((pos[1] - Y_BUF) / 16))

            # TODO: add restart button

            x, y = rel_pos[0], rel_pos[1]
            if rel_pos != (-1, -1):
                board.board_click(x, y, event.button)

            if board.is_finished():
                print("GAME OVER: VICTORY")
                # pygame.quit()
                # sys.exit()

            board.draw(DISPLAYSURF)


            pygame.display.update()

if __name__=="__main__":
    # call the main function
    main()

