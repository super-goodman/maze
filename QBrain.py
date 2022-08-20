
import numpy as np
import pandas as pd


class QLearning:
    #learningRate:α，rewardDecay:γ
    def __init__(self, actions, learningRate=0.01, rewardDecay=0.98, eGreedy=1):
        self.actions = actions  # a list
        self.Alpha = learningRate
        self.gamma = rewardDecay
        self.epsilon = eGreedy
        self.qTable = pd.DataFrame(columns=self.actions, dtype=np.float64)

    def choose_action(self, observation):
        self.check_state_exist(observation)  #if qTable has observation
        # action selection
        if np.random.uniform() < self.epsilon:
            # choose best action
            
            state_action = self.qTable.loc[observation, :]
            print("-----------------",observation,"+++++",state_action,"---------------")
            # some actions may have the same value, randomly choose on in these actions
            action = np.random.choice(state_action[state_action == np.max(state_action)].index)
        else:
            # choose random action
            action = np.random.choice(self.actions)
        return action

    def learn(self, s, a, r, s_):
        self.check_state_exist(s_)  
        qPredict = self.qTable.loc[s, a]
        print(qPredict)
        if s_ != 'terminal':
            qTarget = r + self.gamma * self.qTable.loc[s_, :].max()  # next state is not terminal
        else:
            qTarget = r  # next state is terminal
        self.qTable.loc[s, a] += self.Alpha * (qTarget - qPredict)  # update

    def check_state_exist(self, state):     # walked?
        if state not in self.qTable.index:     # index is raw
            # append new state to q table
            self.qTable = self.qTable.append(
                pd.Series(
                    [0]*len(self.actions),      # [0]*n stands n dementional, 0 vector    表示n维0向量
                    index=self.qTable.columns,   #  [0,1,2,3]
                    name=state,                  #  which grid
                )
 
            )
        