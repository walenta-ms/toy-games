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

revealed_safes = 0

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
def click_over_adj(i, j, tileses):
    acc = []
    x_size = len(tileses)
    y_size = len(tileses[0])

    for x in range(max(0, i - 1), min(x_size, i + 2)):
        for y in range(max(0, j - 1), min(y_size, j + 2)):
            if (x, y) != (i, j):
                ret = tileses[x][y].click(1)
                if ret == 1:
                    acc += [(x, y)]
    return acc

def click_over_adj_rec(i, j, tileses):
    zeroes = click_over_adj(i, j, tileses)
    while zeroes:
        fst = zeroes.pop()
        zeroes += click_over_adj(fst[0], fst[1], tileses)


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
    
    def click(self, pressed):
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

    def l_click(self):
        '''never call directly (will not check for revealed)'''
        global revealed_safes
        if self.img == FLAG:
            return 0
        # elif self.img == self.revealed_img: # SHOULD NEVER REACH THIS
        #     return 0 # return 0 means normal safe click
        elif self.revealed_img == number_files[0]:
            self.revealed = True
            self.img = self.revealed_img
            revealed_safes += 1
            return 1 # return 1 means click hit an empty tiles
        else:
            self.revealed = True
            self.img = self.revealed_img
            revealed_safes += 1
            return 0
    
    def click(self, pressed):
        if self.revealed:
            return 2 # RETURN CODE 2 means they clicked a revealed tile
        if pressed == 1:
            return self.l_click()
        elif pressed == 3:
            return self.r_click()

# class RestartButton(Button):
#     None
    # define right-click as an empty return for this button

def main():
    pygame.init()
    logo = pygame.image.load("mines/moods/happy.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("basic display")

    # X_AX = 16
    # Y_AX = 16
    # TOTAL_MINES = 40

    X_AX = 10
    Y_AX = 8
    TOTAL_MINES = 5

    DARK_GREY = (65, 65, 65)
    GREY = (100, 100, 100)

    DISPLAYSURF = pygame.display.set_mode((X_AX * 16 + 20, Y_AX * 16 + 20))
    DISPLAYSURF.fill(GREY)
    FPS = pygame.time.Clock()
    FPS.tick(60)
    X_BUF = 10
    Y_BUF = 10
    
    board = set_board(X_AX, Y_AX, 5)
    print(board)
    # BOARD INDEX (i, j) MAPS TO TILESES INDEX (j, i) BECAUSE OTHERWISE YOU'D BE
    # INDEXING TILES BY (y, x) (I think? that might make absolutely zero sense)
    # okay transposed the board so hopefully everything is okay now
    draob = np.transpose(board)
    # print(draob)
    safes = 0
    tileses = [[] for i in range(X_AX)]
    for x in range(len(draob)):
        for y in range(len(draob[x])):
            if draob[x, y] == -1:
                tileses[x] += [MineTile((16 * x + X_BUF, 16 * y + Y_BUF))] # add mine
            else:
                tileses[x] += [SafeTile((16 * x + X_BUF, 16 * y + Y_BUF), draob[x, y])] # add safe
                safes += 1

    global revealed_safes
    revealed_safes = 0

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
                # pressed = pygame.mouse.get_pressed()
                # print(pressed)
                pos = pygame.mouse.get_pos()
                rel_pos = (int((pos[0] - X_BUF) / 16), int((pos[1] - Y_BUF) / 16))

            # TODO: add restart button

            if rel_pos[0] > -1 and rel_pos[1] > -1 and rel_pos[0] < X_AX and rel_pos[1] < Y_AX:
                # print(rel_pos)
                x, y = rel_pos[0], rel_pos[1]
                keys_pressed = pygame.key.get_pressed()
                ctrl_click = keys_pressed[pygame.K_RCTRL] or keys_pressed[pygame.K_LCTRL]
                if ctrl_click:
                    ret = tileses[x][y].click(3)
                else:
                    ret = tileses[x][y].click(event.button)
                if ret == 1:
                    click_over_adj_rec(x, y, tileses)
                if ret == 2:
                    # True if #flags around SafeTile == #mines around SafeTile
                    flags_mines_eq = over_adj(x, y, tileses, lambda t : t.img == FLAG) == tileses[x][y].mine_num
                    if flags_mines_eq:
                        click_over_adj_rec(x, y, tileses)

                if ret == -1:
                    print('yeah you lost')
                    for i in range(X_AX): # CHANGE 16 TO VAR
                        for j in range(Y_AX): # CHANGE 16 TO VAR
                            tileses[i][j].reveal()


            # TODO: add a protocol for when click() returns -1
            if revealed_safes == safes:
                print("GAME OVER: VICTORY")
                pygame.quit()
                sys.exit()

            # test.update()
            for tiles in tileses:
                for tile in tiles:
                    tile.draw(DISPLAYSURF)


            pygame.display.update()

if __name__=="__main__":
    # call the main function
    main()

