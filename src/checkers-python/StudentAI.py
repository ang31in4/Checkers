import time
import random
import copy
from collections import defaultdict
from BoardClasses import Move
from BoardClasses import Board
# The following part should be completed by students.
# Students can modify anything except the class name and existing functions and variables.

def capture_count(board, opp_color):
    """
    Given a move made on the board, check if the opponent can make any
    captures after the move
    """
    count = 0
    possible_moves = board.get_all_possible_moves(opp_color)
    for piece in possible_moves:
        for move in piece:
            start = move[0]
            target = move[1]
            largest_net_movement = max(abs(start[0]-target[0]), abs(start[1]-target[1]))
            if largest_net_movement > 1:
                # opponent piece is able to make a capture
                count += largest_net_movement
    return count

def filter_moves(board, my_color, opp_color):
    """
    Filter out moves from all_possible_moves that result in a piece being
    captured. If no moves can be made without a capture, return moves that
    result in the least amount of captures
    """
    result = []
    captures = defaultdict(list)  # {net_movement : [moves]}
    my_moves = board.get_all_possible_moves(my_color)
    for piece in my_moves:
        for move in piece:
            board_copy = copy.deepcopy(board)
            board_copy.make_move(move, my_color)
            score = capture_count(board_copy, opp_color)
            if score > 0:
                # making move results in piece getting captured; filter out move
                # and keep track of how many pieces got captured
                captures[score].append(move)
            else:
                # move is safe to make
                result.append(move)

    # return list of moves that don't result in captures (or list of moves
    # that result in the least amount of captures)
    if not result:
        return captures[sorted(captures.keys())[0]]
    return result


def find_capture_moves(all_moves):
    """
    Returns a list of moves that can capture opponent pieces.
    """
    capture_moves = []  # List to store all capture moves
    best_move_len = 2  # Minimum move length for capturing

    # Check all pieces to see if any of them can capture opponent pieces
    for piece in all_moves:
        for move in piece:
            if len(move) >= best_move_len:
                if len(move) > best_move_len:
                    # Move captures the most pieces; append it
                    best_move_len = len(move)
                    capture_moves.append(move)
                elif best_move_len == 2:
                    # Check for capture moves (distance > 2)
                    start = move[0]
                    target = move[1]
                    if abs(start[0] - target[0]) + abs(start[1] - target[1]) > 2:
                        # This is a valid capture move, append it
                        capture_moves.append(move)

    return capture_moves

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


    def get_move(self, move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1


        entire_move_list = self.board.get_all_possible_moves(self.color)

        # Find capture moves
        capture_moves = find_capture_moves(entire_move_list)

        # Find safe moves
        safe_moves = filter_moves(self.board, self.color, self.opponent[self.color])
        if safe_moves is None:
            safe_moves = []

        # Look for capture moves that are safe
        intersected_moves = [move for move in capture_moves if move in safe_moves]

        if len(intersected_moves) == 1:
            self.board.make_move(intersected_moves[0], self.color)
            return intersected_moves[0]
        elif len(intersected_moves) > 1:
            return self.mcts(entire_move_list, intersected_moves)

        return self.mcts(entire_move_list, safe_moves)

    def mcts(self, active_move_list, filtered_move_list):
        """
        Uses Monte Carlo Tree to determine next best move. Filters
        out bad moves using `filter_moves` and runs simulations on
        the remaining moves.A number of simulations are ran for each
        possible move and a win-rate is determined. The move with
        the highest win-rate is chosen.

        :return: best move found through MCTS
        """
        if len(filtered_move_list) > 0:
            unpacked_list = filtered_move_list
        else:
            unpacked_list = []
            for row in active_move_list:
                for move in row:
                    unpacked_list.append(move)

        # Set up MCTS parameters
        best_move = None
        best_win_rate = -1
        simulations_total = 1000
        simulations_per_move = simulations_total // len(active_move_list)
        time_limit = 15

        start_time = time.time()

        for move in unpacked_list:
            wins = 0
            total_simulations = 0
            good_position = True

            # Run simulations for every possible move, while keeping under time limit
            while total_simulations < simulations_per_move and good_position and (time.time() - start_time) < time_limit:
                # Early pruning using evaluation function
                good_position = self.evaluate_board(move)
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


    def evaluate_board(self, move) -> bool:
        """
        Evaluates the current board state using a simple heuristic.
        Higher scores favor the AI, lower scores favor the opponent.

        :return: A numerical score representing board strength.
        """
        temp_board = copy.deepcopy(self.board)  # Create a copy of current board
        temp_board.make_move(move, self.color)  # Make parameter node AI's first move

        ai_pieces = 0
        ai_kings = 0
        opponent_pieces = 0
        opponent_kings = 0
        ai_score = 0
        opponent_score = 0

        for r in range(temp_board.row):
            for c in range(temp_board.col):
                piece = temp_board.board[r][c]  # Get the piece at position (r, c)
                if piece == self.color:  # AI's normal piece
                    ai_pieces += 1
                    ai_score += 5
                    if 2 <= r < temp_board.row - 2:  # Reward center control
                        ai_score += 2
                    if c == 0 or c == temp_board.col - 1:  # Penalize pieces on the leftmost or rightmost columns
                        ai_score -= 3
                    if r < 2 or r > temp_board.row - 3:  # Encourage backline or deep push
                        ai_score += 4

                    # Reward advancing pieces (aggressive push towards opponent)
                    if r < temp_board.row // 2:
                        ai_score += 1

                    # Reward pieces that are threatening an opponent piece
                    if any(temp_board.board[r + dr][c + dc] == self.opponent[self.color]
                           for dr, dc in [(1, 1), (1, -1)]):
                        ai_score += 3

                    # Penalize exposed pieces (that can be captured by the opponent)
                    if any(temp_board.board[r + dr][c + dc] == self.opponent[self.color]
                           for dr, dc in [(-1, 1), (-1, -1)]):  # Opponent's piece can capture
                        ai_score -= 5

                elif piece == self.color + 2:  # AI's king
                    ai_kings += 1
                    ai_score += 10
                    # Kings are aggressive if closer to the opponent's side
                    if r < temp_board.row // 2:
                        ai_score += 2
                    # Reward kings that are threatening opponent pieces
                    if any(temp_board.board[r + dr][c + dc] == self.opponent[self.color] + 2
                           for dr, dc in [(1, 1), (1, -1)]):
                        ai_score += 5

                    # Penalize kings in vulnerable positions (can be captured)
                    if any(temp_board.board[r + dr][c + dc] == self.opponent[self.color]
                           for dr, dc in [(-1, 1), (-1, -1)]):  # Opponent's piece can capture
                        ai_score -= 3

                elif piece == self.opponent[self.color]:  # Opponent's normal piece
                    opponent_pieces += 1
                    opponent_score += 5
                    if 2 <= r < temp_board.row - 2:
                        opponent_score += 2

                elif piece == self.opponent[self.color] + 2:  # Opponent's king
                    opponent_kings += 1
                    opponent_score += 10

        # Additional scoring for captures (aggressive actions)
        possible_moves = temp_board.get_all_possible_moves(self.color)
        for move_list in possible_moves:
            for move in move_list:
                if len(move[1]) > 1:  # Multi-jump capture
                    ai_score += 15

        temp_score = ai_score - opponent_score  # Positive is good for AI, negative is bad
        if temp_score < -10:  # If the move results in a bad position, assume a loss
            return False
        else:
            return True


    def simulate_game(self, move):
        """
        Runs a simulation of a checkers game using the parent node as the first move.

        :param move: parent node move
        :return: the number of the player that won
        """
        temp_board = copy.deepcopy(self.board)  # Create a copy of current board
        temp_board.make_move(move, self.color)  # Make parameter node AI's first move
        current_player = self.opponent[self.color]  # Give opponent next move

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