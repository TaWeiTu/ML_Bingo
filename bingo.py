import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import random

f = open("record-170328-4.txt", "w")

class Bingo(object):

    def __init__(self):
        self.board = [[[0 for i in range(4)] for j in range(4)] for k in range(4)]
        self.height = [[0 for i in range(4)] for j in range(4)]

        # player = 1 for the player who play first and player = 2 for the opposite
        self.player = 1

    def place(self, row, col):
        '''
        place a cube on position(height, row, col), and return whether the operation is valid
        '''
        # if the position is already taken
        height = self.height[row][col]
        
        if height >= 4:
            return False

        if self.board[height][row][col] != 0:
            return False

        # if there's no placed cube underneath out position
        if height > 0 and self.board[height - 1][row][col] == 0:
            return False

        # place the cube
        self.board[height][row][col] = self.player
        self.change_player()

        self.height[row][col] += 1

        return True

    def full(self):
        for r in range(4):
            for c in range(4):
                if self.height[r][c] < 4:
                    return False
        return True

    def play(self, row, col):

        if self.full():
            print("Draw")
            f.write("Draw")
            return 3

        if not self.place(row, col):
            return -1

        f.write("[{}, {}, {}]".format(self.height[row][col] - 1, row, col))

        if self.win(1):
            print("Player1 win")
            f.write("Player1 win")
            return 1
        
        if self.full():
            print("Draw")
            f.write("Draw")
            return 3

        r, c = self.generate_move()
        while not self.place(r, c):
            r, c = self.generate_move()

        f.write("[{}, {}, {}], ".format(self.height[r][c] - 1, r, c))

        if self.win(2):
            print("Player2 win")
            f.write("Player2 win")
            return 2

        if self.full():
            print("Draw")
            f.write("Draw")
            return 3

        return 0
        

    def plot(self):
        for r in range(4):
            for h in range(4):
                print(" | ", end='')
                for c in range(4):
                    print(self.board[h][r][c], end='')
            print()

    def change_player(self):
        '''
        switch player
        '''
        if self.player == 1:
            self.player = 2
        else:
            self.player = 1

    def win(self, player):
        '''
        return True if player won, False otherwise by checking all possible winning combination
        '''
        for h in range(4):
            for r in range(4):
                flag = True
                for c in range(4):
                    if self.board[h][r][c] != player:
                        flag = False
                if flag:
                    return True

        for h in range(4):
            for c in range(4):
                flag = True
                for r in range(4):
                    if self.board[h][r][c] != player:
                        flag = False
                if flag:
                    return True

        for r in range(4):
            for c in range(4):
                flag = True
                for h in range(4):
                    if self.board[h][r][c] != player:
                        flag = False
                if flag:
                    return True
        
        for h in range(4):
            flag = True
            for i in range(4):
                if self.board[h][i][i] != player:
                    flag = False
            if flag:
                return True
            flag = True
            for i in range(4):
                if self.board[h][i][3 - i] != player:
                    flag = False
            if flag:
                return True
        
        for r in range(4):
            flag = True
            for i in range(4):
                if self.board[i][r][i] != player:
                    flag = False
            if flag:
                return True
            flag = True
            for i in range(4):
                if self.board[i][r][3 - i] != player:
                    flag = False
            if flag:
                return True

        for c in range(4):
            flag = True
            for i in range(4):
                if self.board[i][i][c] != player:
                    flag = False
            if flag:
                return True
            flag = True
            for i in range(4):
                if self.board[i][3 - i][c] != player:
                    flag = False
            if flag:
                return True
        
        flag = True
        for i in range(4):
            if self.board[i][i][i] != player:
                flag = False
        if flag:
            return True
        flag = True
        for i in range(4):
            if self.board[i][i][3 - i] != player:
                flag = False
        if flag:
            return True  
        flag = True
        for i in range(4):
            if self.board[i][3 - i][i] != player:
                flag = False
        if flag:
            return True
        flag = True
        for i in range(4):
            if self.board[3 - i][i][i] != player:
                flag = False
        if flag:
            return True

        return False

    def restart(self):
        '''
        restart the game
        '''
        self.__init__()

    def generate_move(self):
        '''
        1. if player2 can win
        2. if player1 is going to win
        3. random
        '''
        for h in range(4):
            for r in range(4):
                for c in range(4):
                    if self.board[h][r][c] == 0 and (h == 0 or self.board[h - 1][r][c] != 0):
                        self.board[h][r][c] = 2
                        move = False
                        if self.win(2):
                            move = True
                        self.board[h][r][c] = 0
                        if move:
                            return r, c

        for h in range(4):
            for r in range(4):
                for c in range(4):
                    if self.board[h][r][c] == 0 and (h == 0 or self.board[h - 1][r][c] != 0):
                        self.board[h][r][c] = 1
                        move = False
                        if self.win(1):
                            move = True
                        self.board[h][r][c] = 0
                        if move:
                            return r, c
        
        return random.randint(0, 3), random.randint(0, 3)


class MDP(object):
    '''
    Markov Decision Process
    which can be represented as M(S, D, A, P, gamma, R)
    '''
    def __init__(self, reward_function):
        # R(s, a) is the reward obtaining by taking action a at state s
        self.R = reward_function
        self.bingo = Bingo()

    def get_initial_state(self):
        '''
        Refresh the game and return the Initial state s0 based on D
        '''
        self.bingo.restart()
        return np.zeros(shape=[1, 64])

    def get_state(self):
        '''
        Return current state, which is a 4x4x4 bingo board, and compress it to a 1D array for the sake of simplicity
        '''
        state = np.zeros(shape=[1, 64])
        ind = 0
        for h in range(4):
            for r in range(4):
                for c in range(4):
                    state[0][ind] = self.bingo.board[h][r][c]
                    ind += 1

        return state

    def get_reward(self, s, flag):
        '''
        Return the reward of taking action a at state s
        '''
        return self.R(s, flag)

    def take_action(self, action):
        '''
        Take action and Return whether the action is valid, whether the player win or not, new state and the reward
        '''
        row, col = action
        flag = self.bingo.play(row, col)

        new_state = self.get_state()
        reward = self.get_reward(new_state, flag)

        return flag, new_state, reward


class Qlearning(object):
    
    def __init__(self, n_epoch, learning_rate, gamma, reward_function):

        # number of epoches
        self.n_epoch = n_epoch
        # Learning rate between 0 to 1
        self.lr = learning_rate
        # Discount factor between 0 to 1
        self.gamma = gamma
        # R(s) is the reward obtain by achieving state s
        self.reward_function = reward_function
        
        self.MDP = MDP(reward_function)

        # Neuron Network Setup
        self.inp = tf.placeholder(shape=[1,64], dtype=tf.float32)
        self.W = tf.Variable(tf.random_uniform([64, 16], 0, 0.1))
        self.Q = tf.matmul(self.inp, self.W)
        self.predict = tf.argmax(self.Q, 1)

        self.Q_update = tf.placeholder(shape=[1,16], dtype=tf.float32)
        self.loss = tf.reduce_sum(tf.square(self.Q - self.Q_update))
        self.trainer = tf.train.GradientDescentOptimizer(self.lr)
        self.model = self.trainer.minimize(self.loss)
    
    def decode_action(self, action_num):
        action = [0, 0]
        for i in range(2):
            action[i] = action_num % 4
            action_num //= 4
        return action

    def learn(self):
        
        init = tf.initialize_all_variables()

        reward_list = []
        AI_win = 0

        graph_x = np.zeros(self.n_epoch)
        graph_y = np.zeros(self.n_epoch)

        with tf.Session() as sess:
            sess.run(init)

            for epoch in range(self.n_epoch):

                print("Game {}".format(epoch + 1))
                f.write("New Game")
                s = self.MDP.get_initial_state()
                reward = 0
                game_over = False
                fail = False

                while game_over is False:
                    _, Q_val = sess.run([self.predict, self.Q], feed_dict={self.inp: s})
                    Q_slice = Q_val[0, :]

                    action = sorted([i for i in range(16)], key=lambda k:Q_slice[k], reverse=True)

                    flag, new_s, R = 0, 0, 0

                    valid_action = 0

                    for a in action:
                        flag, new_s, R = self.MDP.take_action(self.decode_action(a))
                        if flag != -1:
                            valid_action = a
                            break
                
                    if flag == 1 or flag == 2 or flag == 3:
                        if flag == 1:
                            AI_win += 1
                        game_over = True

                    new_Q = sess.run(self.Q, feed_dict={self.inp: new_s})
                    max_Q = np.max(new_Q)
                    opt_Q = Q_val
                    opt_Q[0, valid_action] = R + self.gamma * max_Q
                    
                    reward += R
                    s = new_s

                    _, new_W = sess.run([self.model, self.W], feed_dict={self.inp: s, self.Q_update: opt_Q})
                
                reward_list.append(reward)
                f.write("\n")

                graph_x[epoch] = epoch
                graph_y[epoch] = AI_win / (epoch + 1) * 100.
    
        return reward_list, graph_x, graph_y



if __name__ == '__main__':

    def main():
        print("n_epoch, lr, gamma:")
        n_epoch = int(input())
        lr = float(input())
        gamma = float(input())

        def reward_function(state, flag):
            if flag == 1:
                return 1
            if flag == 2:
                return -1
            return 0

        Learner = Qlearning(n_epoch, lr, gamma, reward_function)
        _, graph_x, graph_y = Learner.learn()

        plt.plot(graph_x, graph_y)
        plt.show()

        f.close()

    main()
