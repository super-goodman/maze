import numpy as np
import pickle
import pygame as pg

SW = 800
SH = 800
SIZE = 10
SCALING = SW // SIZE
class Snake:
    def __init__(self):
        self.x = 8
        self.y = 7
        self.size = 3
        self.dir = 1  #d irections are 0-up, 1-right, 2-down, 3-left
        self.ate = False
        self.body = []
        for i in range(self.size):
            self.body.append((self.x-i, self.y-i))

    def move(self):
        if self.dir % 2 == 0:
            if self.dir > 0:
                self.y += 1
            else:
                self.y -= 1
        else:
            if self.dir > 1:
                self.x += 1
            else:
                self.x -= 1
        if self.x >= SIZE:  # no walls, snake will go through
            self.x = 0
        elif self.x < 0:
            self.x = SIZE - 1
        if self.y >= SIZE:
            self.y = 0
        elif self.y < 0:
            self.y = SIZE - 1
        if self.ate:
            self.ate = False
            self.body.append(self.body[-1])
        self.body[0] = (self.x, self.y)

        for i in range(len(self.body)):
            if i > 0:
                self.body[-i] = self.body[-i - 1]

    def changeDirection(self, new_dir):
        if abs(self.dir - new_dir) != 2:
            self.dir = new_dir

    def act(self, new_dir):
        if new_dir != self.dir:
            self.changeDirection(new_dir)
        self.move()

    def draw(self, window):
        for part in self.body:
            # Draw rectangle pygame.draw.rect
            
            pg.draw.rect(window, (0, 0, 0),
                         (part[0] * SCALING + 1, part[1] * SCALING + 1, SCALING - 2, SCALING - 2))
         


class Treat:
    def __init__(self):
        self.x = np.random.randint(0, SIZE)
        self.y = np.random.randint(0, SIZE)
    def changePos(self):
        self.x = np.random.randint(0, SIZE)
        self.y = np.random.randint(0, SIZE)
    def draw(self, window):

        pg.draw.rect(window, (0, 255, 255), (self.x * SCALING, self.y * SCALING, SCALING, SCALING))

