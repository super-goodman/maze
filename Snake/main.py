import numpy as np
import pickle
import pygame as pg

# start to use a library pygame, but tkinter is enough
# snake needs a huge table to store states
# however, it is still much easier than chess, because it only has 4 actions in one time

#Time is running, so no module, just write.
SW = 800
SH = 800
SIZE = 10
EPOCHS = 160000
LOSE_PENALTY = 601
EAT_REWARD = 60
MOVE_PENALTY = 3
EPS = 0.7
EPS_DECAY = 0.9997
SHOW_WHEN = 2000
STEPS = 220
LEARNING_RATE = 0.8
DISCOUNT = 0.99
FPS = 60
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

    def changeDirection(self, Dir_):
        if abs(self.dir - Dir_) != 2:
            self.dir = Dir_

    def act(self, Dir_):
        if Dir_ != self.dir:
            self.changeDirection(Dir_)
        self.move()

    def draw(self, window):
        for part in self.body:
            # Draw rectangle pygame.draw.rect
            
            pg.draw.rect(window, (0, 0, 0),
                         (part[0] * SCALING + 1, part[1] * SCALING + 1, SCALING - 2, SCALING - 2))
         


class Food:
    def __init__(self):
        self.x = np.random.randint(0, SIZE)
        self.y = np.random.randint(0, SIZE)

    def draw(self, window):
        pg.draw.rect(window, (0, 255, 255), (self.x * SCALING, self.y * SCALING, SCALING, SCALING))

    def changePos(self):
        self.x = np.random.randint(0, SIZE)
        self.y = np.random.randint(0, SIZE)




class World:
    def __init__(self):
        pg.init()                         # init
        self.clock = pg.time.Clock()      # time
        self.screen = pg.display.set_mode((SW, SH))  # a window  

        self.inside = False    # if food inside of the snake
        self.epochRs = []
        self.suicides = 0
        self.bestMean = -1000
        self.bestQTable = {}
        self.qTable = {}
        self.startingQTable = None


    def initQTable(self):
        if self.startingQTable is None: 
            for xf in range(-SIZE + 1, SIZE):
                for yf in range(-SIZE + 1, SIZE):
                    for lb in range(2):
                        for rb in range(2):
                            for ub in range(2):
                                for db in range(2):
                                    for direction in range(4):
                                        self.qTable[(xf, yf), lb, rb, ub, db, direction] = np.random.uniform(-8, 0, size=4)     #init table

    def isInside(self):
        self.inside = False
        # check the food locatoin :if food is inside of the snake
        for part in self.snake.body:
            if part == (self.food.x, self.food.y):
                self.inside = True
                break

            while self.inside:
                self.inside = False
                self.food.changePos()
                for part in self.snake.body:
                    if part == (self.food.x, self.food.y):
                        self.inside = True
                        break


    def run(self):
        for epoch in range(EPOCHS):
            self.snake = Snake()
            self.food = Food()
            self.isInside()
            #  print log every 500 times
            if not epoch % 500:
                print(f"{epoch}#")
            if epoch < 2:
                FPS = 10
            elif epoch > 2 and epoch <12000:
                FPS = 60
            if epoch % SHOW_WHEN == 0:
                self.render = True
                self.currentMean = np.mean(self.epochRs[-SHOW_WHEN:])
                EPS = 0.8
                print(f"#{epoch}, mean: {self.currentMean}, self.suicides: {self.suicides}, epsilon: {EPS}")
                self.suicides = 0
            else:
                self.render = False
            self.epochRew = 0



            for i in range(STEPS + self.render * 1000):
                self.left = 0
                self.right = 0
                self.up = 0
                self.down = 0

                for part in self.snake.body:

                    if part == (self.snake.x - 1, self.snake.y):                       # x-1 stands go left
                        self.left = 1
                    elif self.snake.x - 1 < 0 and part == (SIZE - 1, self.snake.y):    # go through the left edge
                        self.left = 1
                    if part == ((self.snake.x + 1) % SIZE, self.snake.y):
                        self.right = 1
                    if part == (self.snake.x, self.snake.y - 1):
                        self.up = 1
                    elif self.snake.y - 1 < 0 and part == (self.snake.x, SIZE - 1):
                        self.up = 1
                    if part == (self.snake.x, (self.snake.y + 1) % SIZE):
                        self.down = 1

                self.obs = ((self.snake.x - self.food.x, self.snake.y - self.food.y), self.left, self.right, self.up, self.down, self.snake.dir)  # index of current movement
                if np.random.random() > EPS:
                    self.action = np.argmax(self.qTable[self.obs])                 # max index

                else:
                    self.action = np.random.randint(0, 4)

                self.snake.act(self.action)
                if self.snake.x == self.food.x and self.snake.y == self.food.y:
                    self.snake.ate = True
                    self.food.changePos()
                    self.R = EAT_REWARD
                    self.inside = False
                    self.isInside()

                else:
                    self.R = 0
                    for part in self.snake.body:
                        if part == (self.snake.x, self.snake.y) and part is not self.snake.body[0]:
                            self.R = -LOSE_PENALTY
                            self.suicides += 1
                            break

                    if self.R == 0:
                        self.R = -MOVE_PENALTY
                #
                self.observation_ = ((self.snake.x - self.food.x, self.snake.y - self.food.y), self.left, self.right, self.up, self.down, self.snake.dir)
                self.qPredict = np.max(self.qTable[self.observation_])
                self.qTarget = self.qTable[self.obs][self.action]
                if self.R == EAT_REWARD:
                    self.q_ = EAT_REWARD

                else:
                    self.q_ = (1 - LEARNING_RATE) * self.qTarget + LEARNING_RATE * (self.R + DISCOUNT * self.qPredict)
                self.qTable[self.obs][self.action] = self.q_
                pg.event.get()
                # draw
                if self.render:
                    self.clock.tick(FPS)
                    self.screen.fill((255, 255, 255))
                    self.snake.draw(self.screen)
                    self.food.draw(self.screen)  
                    pg.display.update()
                self.epochRew += self.R
                if self.R == -LOSE_PENALTY:
                    break

            if self.render:
                print(f"snake length {len(self.snake.body) - 2}, did suicides: {self.suicides}")
                # slow down
                #if len(snake.body) > 20:
                    #FPS = 10
            if self.currentMean > self.bestMean:
                self.bestQTable = self.qTable
                self.bestMean = self.currentMean

            self.epochRs.append(self.epochRew)
            EPS *= EPS_DECAY

        pg.quit()

if __name__ == "__main__":

    world = World()
    world.initQTable()
    world.run()

