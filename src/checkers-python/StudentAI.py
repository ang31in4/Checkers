import time
import random
import copy
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and existing functions and variables.
class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2

    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        moves = self.board.get_all_possible_moves(self.color)
        self.board.make_move(move,self.color)
        index = random.randint(0,len(moves)-1)
        inner_index =  random.randint(0,len(moves[index])-1)
        move = moves[index][inner_index]
        return move

    def simulate_game(self, move):
        """
        Runs a simulation of a checkers game using the parent node as the first move.

        :param move: parent node move
        :return: the number of the player that won
        """
        temp_board = copy.deepcopy(self.board) # Create a copy of current board
        temp_board.make_move(move, self.color) # Make parameter node AI's first move
        current_player = self.opponent[self.color] # Give opponent next move

        # Keep playing moves until there is a winner or tie
        while True:
            # Choose a random move
            possible_moves = temp_board.get_all_possible_moves(current_player)
            if not possible_moves:
                break
            random_move = random.choice(random.choice(possible_moves))
            temp_board.make_move(random_move, current_player)

            # Check if the current player has won after their move
            winner = temp_board.is_win(current_player)
            if winner == current_player:
                return current_player  # Return the winner
            elif winner == 0:
                return None # Return None if there is a tie

            current_player = self.opponent[current_player]  # Switch turns

        return None # Return for tie