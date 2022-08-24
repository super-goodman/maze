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
startingQTable = None

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


if __name__ == "__main__":
    pg.init()                    # init
    clock = pg.time.Clock()      # time
    screen = pg.display.set_mode((SW, SH))  # a window
    # =========================================================================
    # observation space is location of food relative to head and is there a body on the left, right or fowards

    if startingQTable is None:
        qTable = {}
        for xtf in range(-SIZE + 1, SIZE):
            for ytf in range(-SIZE + 1, SIZE):
                for lb in range(2):
                    for rb in range(2):
                        for ub in range(2):
                            for db in range(2):
                                for direction in range(4):
                                    qTable[(xtf, ytf), lb, rb, ub, db, direction] = np.random.uniform(-8, 0, size=4)     #init table

    epochRewards = []
    suicides = 0
    bestMean = -1000
    bestQTable = {}

    for epoch in range(EPOCHS + 2):
        python = Snake()
        food = Treat()
        inside = False

        # check the food locatoin :if food is inside of the snake
        for part in python.body:
            if part == (food.x, food.y):
                inside = True
                break

            while inside:
                inside = False
                food.changePos()
                for part in python.body:
                    if part == (food.x, food.y):
                        inside = True
                        break

        #  print log every 500 times
        if not epoch % 500:
            print(f"{epoch}#")
        if epoch < 2:
            FPS = 10
        elif epoch > 2 and epoch <12000:
            FPS = 60
        if epoch % SHOW_WHEN == 0:
            render = True
            currentMean = np.mean(epochRewards[-SHOW_WHEN:])
            print(f"#{epoch}, mean: {currentMean}, suicides: {suicides}, epsilon: {EPS}")
            suicides = 0
        else:
            render = False
        epochRew = 0
        for i in range(STEPS + render * 1000):
            leftB = 0
            rightB = 0
            upB = 0
            downB = 0

            for part in python.body:

                if part == (python.x - 1, python.y):                       # x-1 stands go left
                    leftB = 1
                elif python.x - 1 < 0 and part == (SIZE - 1, python.y):    # go through the left edge
                    leftB = 1
                if part == ((python.x + 1) % SIZE, python.y):
                    rightB = 1
                if part == (python.x, python.y - 1):
                    upB = 1
                elif python.y - 1 < 0 and part == (python.x, SIZE - 1):
                    upB = 1
                if part == (python.x, (python.y + 1) % SIZE):
                    downB = 1

            obs = ((python.x - food.x, python.y - food.y), leftB, rightB, upB, downB, python.dir)  # index of current movement
            if np.random.random() > EPS:
                action = np.argmax(qTable[obs])                 # max index

            else:
                action = np.random.randint(0, 4)

            python.act(action)
            if python.x == food.x and python.y == food.y:
                python.ate = True
                food.changePos()
                reward = EAT_REWARD
                inside = False
                for part in python.body:
                    if part == (food.x, food.y):
                        inside = True
                        break

                while inside:
                    inside = False
                    food.changePos()
                    for part in python.body:
                        if part == (food.x, food.y):
                            inside = True
                            break

            else:
                reward = 0
                for part in python.body:
                    if part == (python.x, python.y) and part is not python.body[0]:
                        reward = -LOSE_PENALTY
                        suicides += 1

                        break

                if reward == 0:
                    reward = -MOVE_PENALTY
            newObservation = ((python.x - food.x, python.y - food.y), leftB, rightB, upB, downB, python.dir)
            maxFutureQ = np.max(qTable[newObservation])
            currentQ = qTable[obs][action]
            if reward == EAT_REWARD:
                newQ = EAT_REWARD

            else:
                newQ = (1 - LEARNING_RATE) * currentQ + LEARNING_RATE * (reward + DISCOUNT * maxFutureQ)
            qTable[obs][action] = newQ
            pg.event.get()

            if render:
                clock.tick(FPS)
    
                screen.fill((255, 255, 255))
    
                python.draw(screen)
                food.draw(screen)  
                pg.display.update()
            epochRew += reward
            if reward == -LOSE_PENALTY:
                break

        if render:
            print(f"snake length {len(python.body) - 2}, did suicide: {suicides}")

            if len(python.body) > 20:
                FPS = 10
        if currentMean > bestMean:
            bestQTable = qTable
            bestMean = currentMean

        epochRewards.append(epochRew)
        EPS *= EPS_DECAY

    pg.quit()
