
from maze_environment import Maze
from QBrain import QLearning
import time


def update():
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
            action = RL.choose_action(str(observation))

            # RL take action and get next observation and reward
            observation_, reward, done = env.step(action)

            # RL learn from this transition
            RL.learn(str(observation), action, reward, str(observation_))

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

if __name__ == "__main__":
    env = Maze()

    RL = QLearning(actions=list(range(env.actionNum)))  #QTable store things

    env.after(1, update)
    env.mainloop()