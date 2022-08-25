

import numpy as np
import sys
import json
import time
import pandas as pd
from requests import put
from distutils.log import debug

if sys.version_info.major == 2:
    import Tkinter as tk
else:
    import tkinter as tk




UNIT = 40   # Unit size
MAZE_H = 8  
MAZE_W = 8  

class QLearning:
    #rewardDecay:γ, learningRate:α
    def __init__(self, actions, learningRate=0.01, rewardDecay=0.98, eGreedy=1):
        self.actions = actions  # a list
        self.Alpha = learningRate
        self.gamma = rewardDecay
        self.epsilon = eGreedy
        self.qTable = pd.DataFrame(columns=self.actions, dtype=np.float64)

    def choose_action(self, observation):
        self.checkStateExist(observation)  #if qTable has observation
        # action selection
        if np.random.uniform() < self.epsilon:
            # choose best action
            
            stateAction = self.qTable.loc[observation, :]
            # some actions may have the same value, randomly choose on in these actions
            action = np.random.choice(stateAction[stateAction == np.max(stateAction)].index)
        else:
            # choose random action
            action = np.random.choice(self.actions)
        return action

    def learn(self, s, a, r, s_):
        self.checkStateExist(s_)  
        qPredict = self.qTable.loc[s, a]
        #print(qPredict)
        if s_ != 'terminal':
            qTarget = r + self.gamma * self.qTable.loc[s_, :].max()  # next state is not terminal
        else:
            qTarget = r  # next state is terminal
        self.qTable.loc[s, a] += self.Alpha * (qTarget - qPredict)  # update

    def checkStateExist(self, state):     # walked?
        if state not in self.qTable.index:     # index is raw
            # append new state to q table
            self.qTable = self.qTable.append(
                pd.Series(
                    len(self.actions)*[0],      # [0]*n stands n dementional, 0 vector   
                    index=self.qTable.columns,   #  [0,1,2,3]
                    name=state,                  #  which grid
                )
 
            )
        

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
        self.configure(bg='red')
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
            "green")
   
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

class World:
    def __init__(self):
        self.RL = QLearning(actions=list(range(env.actionNum)))  #QTable store things
    def update(self):
        count = 0 # timer count
        for episode in range(10000):
            # initial observation
            observation = env.reset()  # coordinatoin of agent
            R = 0  # reward
            time_start = time.time()
            print("-------------------------------------------------------------%d" %episode)
            while True:
        
                # update 
                env.render()

                # RL choose action based on observation
                action = self.RL.choose_action(str(observation))

                # RL take action and get next observation and reward
                observation_, reward, done = env.step(action)

                # RL learn from this transition
                self.RL.learn(str(observation), action, reward, str(observation_))
                # swap observation
                observation = observation_
                if episode > 9000 or count >= 20 or episode < 5:
                    time.sleep(0.1)
                R = R + reward  # add all rewards

                # break while loop when end of this episode
                if done:
                    #slow down when find a best way
    
                    if (time.time()-time_start) < 5 and R >= 70:
                        count += 1
                    else:
                        count = 0
                    print("reward = %d,time = %d"%(R,count))  # show every turn's reward
                    break


        # end of game
        print('game over')
        env.destroy()



if __name__ == '__main__':
    env = Maze()
    world = World()

    env.after(1, world.update())
    env.mainloop()
    