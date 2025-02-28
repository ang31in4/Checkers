import time
import random
import copy
import math
from collections import defaultdict
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

    @staticmethod
    def ucb(win_rate, total_simulations, parent_simulations, c=1.41):
        """
        Calculate the UCB1 score for a move.
        :param win_rate: Win rate of the move
        :param total_simulations: Total simulations for this move
        :param parent_simulations: Total simulations for the parent node
        :param c: Exploration constant
        :return: UCB1 score
        """
        if total_simulations == 0:
            return float('inf')  # Prioritize unexplored moves
        return win_rate + c * math.sqrt(math.log(parent_simulations) / total_simulations)

    def mcts(self):
        """
        Uses Monte Carlo Tree Search with UCB1 to determine the next best move.

        :return: Best move found through MCTS
        """
        possible_moves = self.board.get_all_possible_moves(self.color)
        num_moves = sum(len(move_list) for move_list in possible_moves)

        # If only one move is available, return it immediately
        if num_moves == 1:
            # Find the move and return it immediately
            for move_list in possible_moves:
                if move_list:  # Non-empty list
                    return move_list[0]  # Return the first (and only) move

        # Set up MCTS parameters
        time_limit = 15

        # Start time
        start_time = time.time()

        # Tracking statistics for UCB1
        wins_per_move = defaultdict(int)
        simulations_per_move = defaultdict(int)
        parent_simulations = 0

        # Run MCTS while under time limit
        while (time.time() - start_time) < time_limit:
            best_ucb = -float('inf')
            selected_move = None

            # Calculate UCB1 scores for all moves
            for moves in possible_moves:
                for move in moves:
                    # Calculate UCB1 for this move
                    if simulations_per_move[move] > 0:
                        win_rate = wins_per_move[move] / simulations_per_move[move]
                    else:
                        win_rate = 0

                    ucb_score = self.ucb(win_rate, simulations_per_move[move], parent_simulations)

                    # Select the move with the highest UCB1 score
                    if ucb_score > best_ucb:
                        best_ucb = ucb_score
                        selected_move = move

            # Run a simulation for the selected move
            winner = self.simulate_game(selected_move)
            if winner == self.color:
                wins_per_move[selected_move] += 1

            simulations_per_move[selected_move] += 1
            parent_simulations += 1

        # Choose the move with the highest win rate
        best_move = max(wins_per_move, key=lambda m: wins_per_move[m] / simulations_per_move[m])

        # Make the best move
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
                    if c == 0 or c == self.col - 1:  # Penalize pieces on the leftmost or rightmost columns
                        ai_score -= 3
                    if r < 2 or r > self.row - 3:  # Encourage backline or deep push
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
        temp_board = copy.deepcopy(self.board)  # Create a copy of current board
        temp_board.make_move(move, self.color)  # Make parameter node AI's first move
        current_player = self.opponent[self.color]  # Give opponent next move

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
                return None  # Return None if there is a tie

            current_player = self.opponent[current_player]  # Switch turns

        return None  # Return for tie