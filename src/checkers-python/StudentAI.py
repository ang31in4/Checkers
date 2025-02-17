import time
import random
import copy
from BoardClasses import Move
from BoardClasses import Board
# The following part should be completed by students.
# Students can modify anything except the class name and existing functions and variables.
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

        return self.mcts()


    def mcts(self):
        """
        Uses Monte Carlo Tree to determine next best move. A number of simulations
        are ran for each possible move and a win-rate is determined. The move with
        the highest win-rate is chosen.

        :return: best move found through MCTS
        """
        possible_moves = self.board.get_all_possible_moves(self.color)
        num_moves = sum(len(move_list) for move_list in possible_moves)

        # Set up MCTS parameters
        best_move = None
        best_win_rate = -1
        simulations_total = 1000
        simulations_per_move = simulations_total // num_moves
        time_limit = 15

        start_time = time.time()

        for moves in possible_moves:
            for move in moves:
                wins = 0
                total_simulations = 0

                # Run simulations for every possible move, while keeping under time limit
                while total_simulations < simulations_per_move and (time.time() - start_time) < time_limit:
                    winner = self.simulate_game(move)
                    if winner == self.color:
                        wins += 1
                    total_simulations += 1

                # Calculate win rate
                if total_simulations > 0:
                    win_rate = wins / total_simulations
                else:
                    win_rate = 0

                if win_rate > best_win_rate:
                    best_win_rate = win_rate
                    best_move = move

        # Make move
        self.board.make_move(best_move, self.color)
        return best_move

    def evaluate_board(self):
        """
        Evaluates the current board state using a simple heuristic.
        Higher scores favor the AI, lower scores favor the opponent.
        
        :return: A numerical score representing board strength.
        """
        ai_pieces = 0
        ai_kings = 0
        opponent_pieces = 0
        opponent_kings = 0
        ai_score = 0
        opponent_score = 0

        for r in range(self.row):
            for c in range(self.col):
                piece = self.board.board[r][c]  # Get the piece at position (r, c)
                if piece == self.color:  # AI's normal piece
                    ai_pieces += 1
                    ai_score += 5
                    if 2 <= r < self.row - 2:  # Reward center control
                        ai_score += 2
                    if c == 0 or c == self.col - 1: # Penalize pieces on the leftmost or rightmost columns
                        ai_score -= 3
                    if r < 2 or r > self.row - 3: # Encourage backline or deep push
                        ai_score += 4
                elif piece == self.color + 2:  # AI's king
                    ai_kings += 1
                    ai_score += 10
                elif piece == self.opponent[self.color]:  # Opponent's normal piece
                    opponent_pieces += 1
                    opponent_score += 5
                    if 2 <= r < self.row - 2:
                        opponent_score += 2  
                elif piece == self.opponent[self.color] + 2:  # Opponent's king
                    opponent_kings += 1
                    opponent_score += 10

        # Additional scoring for captures
        possible_moves = self.board.get_all_possible_moves(self.color)
        for move_list in possible_moves:
            for move in move_list:
                if len(move[1]) > 1:  # Multi-jump capture
                    ai_score += 15  

        return ai_score - opponent_score  # Positive is good for AI, negative is bad

    def simulate_game(self, move):
        """
        Runs a simulation of a checkers game using the parent node as the first move.

        :param move: parent node move
        :return: the number of the player that won
        """
        temp_board = copy.deepcopy(self.board) # Create a copy of current board
        temp_board.make_move(move, self.color) # Make parameter node AI's first move
        current_player = self.opponent[self.color] # Give opponent next move

        # **Early pruning using evaluation function**
        temp_score = self.evaluate_board()  
        if temp_score < -10:  # If the move results in a bad position, assume a loss
            return self.opponent[self.color]

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