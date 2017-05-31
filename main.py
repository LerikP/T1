import random
import time
import pygame
from pygame.locals import *
import sys
import pdb

GLASS_HEIGHT = 20
GLASS_WIDTH = 10
SCREEN_HEIGHT = 720
SCREEN_WIDHT = 405
CELL_HEIGHT = 25
CELL_WIDTH = 25
X_OFFSET = (SCREEN_WIDHT - CELL_WIDTH * GLASS_WIDTH) // 2
Y_OFFSET = (SCREEN_HEIGHT - CELL_HEIGHT * GLASS_HEIGHT) // 2

FIGURES = [['0000', '0000', '1111', '0000'],
           ['000', '111', '010'],
           ['11', '11'],
           ['000', '110', '011'],
           ['000', '011', '110'],
           ['000', '111', '100'],
           ['000', '111', '001']]

COLORS = [(200, 0, 0, 0), (0, 200, 0, 0), (0, 0, 200, 0)]
DIRECTIONS = {'D': (1, 0), 'U': (-1, 0), 'R': (0, 1), 'L': (0, -1)}
OPPOSITE_DIRECTIONS = {'D': 'U', 'U': 'D', 'R': 'L', 'L': 'R'}
SPEED = 30
MOVESPEED = 6

timer = pygame.time.Clock()


class Cell(object):
    """Contains simple sell """

    def __init__(self, full=False, color=(50, 50, 50, 0)):
        self.full = full
        self.color = color

    def is_full(self):
        return self.full

    def get_color(self):
        return self.color

    def set_full(self, full):
        self.full = full

    def set_color(self, color):
        self.color = color


class Glass(object):
    """Contains glass"""

    def __init__(self):
        self.glass = []
        for line in range(GLASS_HEIGHT):
            self.glass.append([Cell() for c in range(GLASS_WIDTH)])

    def remove_line(self, line):
        for i, l in enumerate(self.glass[line::-1]):
            if i < line:
                self.glass[line - i] = self.glass[line - i - 1][:]
            else:
                self.glass[line - i] = [Cell() for c in range(GLASS_WIDTH)]

    def fill_cell(self, y, x, c):
        if x in range(GLASS_WIDTH) and y in range(GLASS_HEIGHT):
            self.glass[y][x] = c
            return True
        else:
            return False

    def try_place(self, figure):
        for i in range(len(figure.shape)):
            for j in range(len(figure.shape)):
                if figure.shape[i][j] == '1':
                    if (figure.y + i) not in range(GLASS_HEIGHT) or (figure.x + j) not in range(GLASS_WIDTH):
                        return False
                    if self.glass[figure.y + i][figure.x + j].is_full():
                        return False
                    if self.glass[figure.y + i][figure.x + j].is_full():
                        return False
        return True

    def place(self, figure):
        for i in range(len(figure.shape)):
            for j in range(len(figure.shape)):
                if figure.shape[i][j] == '1':
                    self.glass[figure.y + i][figure.x + j].set_full(True)
                    self.glass[figure.y + i][figure.x + j].set_color(figure.color)

    def clear(self, figure):
        for i in range(len(figure.shape)):
            for j in range(len(figure.shape)):
                if figure.shape[i][j] == '1':
                    self.glass[figure.y + i][figure.x + j].set_full(False)
                    self.glass[figure.y + i][figure.x + j].set_color((50, 50, 50, 0))

    def __str__(self):
        return '\n'.join([''.join(str(int(l.is_full())) for l in line) for line in self.glass])

    def __repr__(self):
        return str(self)


class Figure(object):
    """Contains figure"""

    def __init__(self, type_, x=GLASS_WIDTH // 2 - 2, y=0):
        self.color = random.choice(COLORS)
        self.shape = FIGURES[type_]
        self.rotate(random.randint(0, 3))
        self.x = x
        self.y = y

    def rotate(self, count=1):
        for c in range(count):
            self.shape = [s[::-1] for s in zip(*self.shape)]
        return self.shape

    def move(self, direction):
        self.y += DIRECTIONS[direction][0]
        self.x += DIRECTIONS[direction][1]

    def __str__(self):
        return '\n'.join([''.join(l for l in line) for line in self.shape])

    def __repr__(self):
        return str(self)


class PyGame(object):
    """Main game class"""

    def __init__(self, width=SCREEN_WIDHT, height=SCREEN_HEIGHT):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Tetris')
        self.bg = pygame.Surface((self.width, self.height))
        self.bg.fill(Color(0, 0, 0, 0))
        self.glass = Glass()
        self.figure = Figure(random.choice(range(len(FIGURES))))
        self.drop_count = 0
        self.falling = False
        self.end_game = False
        self.gameover_font = pygame.font.Font(None, 70)
        self.direction = ''
        self.move_count = 0
        self.score = 0
        self.score_font = pygame.font.Font(None, 40)

    def main_loop(self):
        while True:
            if not self.end_game:
                self.glass.clear(self.figure)
                timer.tick(60)
                # self.direction = ''
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if event.type == KEYDOWN and event.key == pygame.K_SPACE:
                        self.falling = True
                    if event.type == KEYDOWN and event.key == pygame.K_UP:
                        self.direction = 'U'
                    if event.type == KEYDOWN and event.key == pygame.K_DOWN:
                        self.direction = 'D'
                    if event.type == KEYDOWN and event.key == pygame.K_LEFT:
                        self.direction = 'L'
                    if event.type == KEYDOWN and event.key == pygame.K_RIGHT:
                        self.direction = 'R'
                    if event.type == KEYUP:
                        self.move_count = MOVESPEED
                        self.direction = ''

                self.update(self.direction)
                self.check_destruction()
                self.render()
            else:
                # print('Game ended')
                gameover = self.gameover_font.render('GAME OVER', 0, (255, 255, 255, 0))
                self.screen.blit(gameover, (50, 300))
                pygame.display.update()
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()

    def update(self, direction=''):
        if not self.glass.try_place(self.figure):
            self.end_game = True
        if self.falling:
            while self.glass.try_place(self.figure):
                self.figure.move('D')
            self.figure.move('U')
            self.falling = False
            return
        self.drop_count += 1
        if self.drop_count > SPEED:
            self.drop_count = 0
            self.figure.move('D')
            if not self.glass.try_place(self.figure):
                self.figure.move('U')
                self.glass.place(self.figure)
                self.score += 10
                self.figure = Figure(random.choice(range(len(FIGURES))))
                if not self.glass.try_place(self.figure):
                    self.end_game = True
                return

        self.move_count += 1
        if self.move_count >= MOVESPEED:
            self.move_count = 0
            if direction == 'U':
                self.figure.rotate()
                if not self.glass.try_place(self.figure):
                    self.figure.rotate(3)
            elif direction in DIRECTIONS:
                self.figure.move(direction)
                if not self.glass.try_place(self.figure):
                    self.figure.move(OPPOSITE_DIRECTIONS[direction])

    def render(self):
        self.screen.blit(self.bg, (0, 0))
        score = self.score_font.render('SCORE: {}'.format(self.score), 0, (255, 255, 255, 0))
        self.screen.blit(score, (110, 20))
        for y, line in enumerate(self.glass.glass):
            for x, c in enumerate(line):
                cell = pygame.Surface((CELL_WIDTH, CELL_HEIGHT))
                cell.fill(Color(*c.get_color()))
                self.screen.blit(cell, (x * CELL_WIDTH + X_OFFSET, y * CELL_HEIGHT + Y_OFFSET))
        if not self.end_game:
            for y, line in enumerate(self.figure.shape):
                for x, c in enumerate(line):
                    cell = pygame.Surface((CELL_WIDTH, CELL_HEIGHT))
                    if c == '1':
                        cell.fill(Color(*self.figure.color))
                        self.screen.blit(cell, ((self.figure.x + x) * CELL_WIDTH + X_OFFSET,
                                                (self.figure.y + y) * CELL_HEIGHT + Y_OFFSET))
        pygame.display.update()
        # print(self.glass)
        # print()

    def check_destruction(self):
        bonus = 0
        for l, line in enumerate(self.glass.glass):
            if all(c.is_full() for c in line):
                self.glass.remove_line(l)
                bonus += 1
        self.score += (bonus ** 2) * 100


if __name__ == '__main__':
    window = PyGame()
    window.main_loop()

    # g = Glass()
    # f = Figure(1)
    # for line in range(GLASS_HEIGHT):
    #     for c in range(GLASS_WIDTH):
    #         g.fill_cell(line, c, Cell(random.choice((True, False))))
    # while g.try_place(f):
    #     f.move('D')
    # f.move('U')
    # g.place(f)
    # pdb.set_trace()
    # print(g)
    # g.try_place(f)


# print(DIRECTIONS['D'])
# g = Glass()

# print(g)
# print()
# g.remove_line(0)
# print(g)


# f = Figure(random.randint(0, 4))
# print(f)
# print()
# f.rotate(1)
# print(f)
# print()
# f.rotate(1)
# print(f)
# print()
# f.rotate(1)
# print(f)
# print()
# f.rotate(1)
# print(f)
# print()
# f.rotate(1)
# print(f)
# print()
# f.rotate(1)
# print(f)

# t = g.try_place(f)
# print(t)

# if t:
#     g.place(f)
# print(g)
# print()

# while True:
#     # move = input()
#     move = random.choice(list(DIRECTIONS.keys()))
#     if move in DIRECTIONS:
#         g.clear(f)
#         print(move)
#         f.move(*DIRECTIONS[move])
#         if g.try_place(f):
#             g.place(f)
#         else:
#             f.move(*DIRECTIONS[OPPOSITE_DIRECTIONS[move]])
#             continue
#         print(g)
#         print()

#     elif move == 'Q':
#         break
#     else:
#         continue
#     time.sleep(1)
#     if random.random() < 0.1:
#         print('Stored')
#         f = Figure(random.randint(0, 4))
#         if not g.try_place(f):
#             print('Could not place new figure')
#             break
