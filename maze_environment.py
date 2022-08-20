
from distutils.log import debug
import numpy as np
import time
import sys
import json

from requests import put

if sys.version_info.major == 2:
    import Tkinter as tk
else:
    import tkinter as tk




UNIT = 40   # Unit size
MAZE_H = 8  
MAZE_W = 8  


class Maze(tk.Tk, object):
    def __init__(self):
        super(Maze, self).__init__()
        self.mazeFilePath = "mazeData/mazeData.json"
        self.actionSpace = ['u', 'd', 'l', 'r']
        self.actionNum = len(self.actionSpace)
        self.title('maze')
        self.geometry('{0}x{1}'.format(MAZE_H * UNIT, MAZE_H * UNIT))
        self.caveList = []
        self.buildMaze()
        self.showPath = True

    # read json file
    def readJson(self):
        f = open(self.mazeFilePath, mode='r')
        data = json.load(f)
        f.close()
        return data


    # put things on
    def put(self,func,coor,color):
        return func(
        coor[0],coor[1],
        coor[2],coor[3],
        fill=color)

    def buildMaze(self):
        self.canvas = tk.Canvas(self, bg='white',
                           height=MAZE_H * UNIT,
                           width=MAZE_W * UNIT)

        # create grids
        for c in range(0, MAZE_W * UNIT, UNIT):
            x0, y0, x1, y1 =c, 0, c, MAZE_H * UNIT
            self.canvas.create_line(x0, y0, x1, y1)
        for r in range(0, MAZE_H * UNIT, UNIT):
            x0, y0, x1, y1 = 0, r, MAZE_W * UNIT , r
            self.canvas.create_line(x0, y0, x1, y1)

        # create origin
        origin = np.array([20, 20])

        # read mazeData
        # read cave data
        self.jsonData = self.readJson()
        lens = len(self.jsonData["maze"])
        for i in range(lens-1):    
            self.caveList.append(self.canvas.coords(self.put(self.canvas.create_rectangle,
            self.jsonData["maze"][i][str(i)],
            "black")))

        # create target
        self.oval = self.put(self.canvas.create_oval,
            self.jsonData["maze"][lens-1]['t'],
            "yellow")
   
        # create red rect
        self.rect = self.canvas.create_rectangle(
            origin[0] - 15, origin[1] - 15,
            origin[0] + 15, origin[1] + 15,
            fill='red')

        # pack all
        self.canvas.pack()

    def reset(self):
        self.update()
        #time.sleep(0.5)
        self.canvas.delete(self.rect)
        origin = np.array([20, 20])
        self.rect = self.canvas.create_rectangle(
            origin[0] - 15, origin[1] - 15,
            origin[0] + 15, origin[1] + 15,
            fill='red')
        # return observation
        return self.canvas.coords(self.rect)

    def step(self, action):
        s = self.canvas.coords(self.rect)
        baseAction = np.array([0, 0])
        if action == 0:   # up
            if s[1] > UNIT:
                baseAction[1] -= UNIT
        elif action == 1:   # down
            if s[1] < (MAZE_H - 1) * UNIT:
                baseAction[1] += UNIT
        elif action == 2:   # right
            if s[0] < (MAZE_W - 1) * UNIT:
                baseAction[0] += UNIT
        elif action == 3:   # left
            if s[0] > UNIT:
                baseAction[0] -= UNIT

        self.canvas.move(self.rect, baseAction[0], baseAction[1])  # move agent
        s_ = self.canvas.coords(self.rect)  # next state

        # reward function
        if s_ == self.canvas.coords(self.oval):
            reward = 100
            done = True
            s_ = 'terminal'
            #time.sleep(0.01)

        # punishment
        elif s_ in self.caveList: 
            reward = -100   # reward
            done = True
            s_ = 'terminal'
        else:
            reward = -1
            done = False

        return s_, reward, done


    def render(self):
    
        # time.sleep(0.1)
        self.update()




if __name__ == '__main__':
    env = Maze()
    env.mainloop()
    