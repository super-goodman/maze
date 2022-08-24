
from ctypes.wintypes import UINT
from re import I
from unittest import case
import numpy as np
import time
import sys
import json

if sys.version_info.major == 2:
    import Tkinter as tk
else:
    import tkinter as tk

UNIT = 40   # UNIT size
MAZE_H = 8  # maze height
MAZE_W = 8  # maze width

class Maze(tk.Tk, object):
    def __init__(self):
        # init window
        super(Maze, self).__init__()
        self.mazeFilePath = "mazeData/mazeData.json"
        self.title('maze')
        self.geometry('{0}x{1}'.format(MAZE_H * UNIT, MAZE_H * UNIT))
        self.buildMaze()

        #json
        self.count = 0
        self.f = open(self.mazeFilePath, mode='w')
        self.jsonData = {"maze":[ ]}
  

    # wall move
    def step(self,action):
        s = self.canvas.coords(self.rect)
        baseAction = np.array([0, 0])
        if action == 0:   # up
            if s[1] > UNIT:
                baseAction[1] -= UNIT
        elif action == 1:   # down
            if s[1] < (MAZE_H - 1) * UNIT:
                baseAction[1] += UNIT
        elif action == 2:   #left
            if s[0] > UNIT:
                baseAction[0] -= UNIT
        elif action == 3:   # right
            if s[0] < (MAZE_W - 1) * UNIT:
                baseAction[0] += UNIT
        # move self
        self.canvas.move(self.rect, baseAction[0], baseAction[1])  # move agent
        
    # save json file
    def saveJson(self,name,coor):
        self.jsonData["maze"].append({name:coor})
    

    # put things on
    def put(self,func,coor,color):
            s = self.canvas.coords(coor)
            self.hell1 = func(
            s[0],s[1],
            s[2],s[3],
            fill=color)
            return s

    # key callback
    def key(self,event):
        print(event.keycode)
        if event.keycode == 8320768:
            #print("UP")
            self.step(0)
        elif event.keycode == 8255233:
            #print("DOWN")
            self.step(1)
        elif event.keycode == 8124162:
            #print("LEFT")
            self.step(2)
        elif event.keycode == 8189699:
            #print("RIGHT")
            self.step(3)
        elif event.keycode == 2359309:
            #print("ENTER")
            coor = self.put(self.canvas.create_rectangle,self.rect,"black")

            # save Json
            self.saveJson('%d'%self.count,coor)
            self.count += 1
        elif event.keycode == 47:
            #print("put target(?)")
            coor = self.put(self.canvas.create_oval,self.rect,"yellow")
            # save Json
            self.saveJson('t',coor)
            self.jsonData = json.dumps(self.jsonData)
            self.f.write(self.jsonData)
            self.f.close()
            exit(0)
       


    # build maze frame
    def buildMaze(self):
        self.canvas = tk.Canvas(self, bg='white',
                           height=MAZE_H * UNIT,
                           width=MAZE_W * UNIT)


        # # create grids
        # for c in range(0, MAZE_W * UNIT, UNIT):
        #     x0, y0, x1, y1 =c, 0, c, MAZE_H * UNIT
        #     self.canvas.create_line(x0, y0, x1, y1)
        # for r in range(0, MAZE_H * UNIT, UNIT):
        #     x0, y0, x1, y1 = 0, r, MAZE_W * UNIT , r
        #     self.canvas.create_line(x0, y0, x1, y1)

        # create origin
        origin = np.array([20, 20])
        # create red rect
        self.rect = self.canvas.create_rectangle(
            origin[0] - 15, origin[1] - 15,
            origin[0] + 15, origin[1] + 15,
            fill='red')


        # keyboard monitor
        self.canvas.focus_set()
        self.canvas.bind("<Key>", self.key)

       # pack all
        self.canvas.pack()




if __name__ == "__main__":
    env = Maze()
    env.mainloop()