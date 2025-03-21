import math
import copy
import time
import argparse

class MiniChess:
    
    def __init__(self):
        self.current_game_state = self.init_board()

        (self.timeout,
         self.max_turns,
         self.white_ai,
         self.black_ai,
         self.alphabeta,
         self.heuristic,
         self.depth) = self.set_parameters()
        (self.states_visited_per_depth,
         self.non_leaf_nodes,
         self.total_nodes) = self.set_stats()

    """
    Initialize the board

    Args:
        - None
    Returns:
        - state: A dictionary representing the state of the game
    """
    def init_board(self):
        state = {
                "board": 
                [['bK', 'bQ', 'bB', 'bN', '.'],
                ['.', '.', 'bp', 'bp', '.'],
                ['.', '.', '.', '.', '.'],
                ['.', 'wp', 'wp', '.', '.'],
                ['.', 'wN', 'wB', 'wQ', 'wK']],
                "turn": 'white',
                "game_over_reason": '',
                "turn_number": 1,
                "turns_without_capture": 0,
                "turn_no_capture": False
                }
        return state

    """
    Prints the board
    
    Args:
        - game_state: Dictionary representing the current game state
    Returns:
        - None
    """
    def display_board(self, game_state):
        print()
        for i, row in enumerate(game_state["board"], start=1):
            print(str(6-i) + "  " + ' '.join(piece.rjust(3) for piece in row))
        print()
        print("     A   B   C   D   E")
        print()

    @staticmethod
    def get_formatted_board(game_state):
        board_substrings = []
        for i, row in enumerate(game_state["board"], start=1):
            board_substrings.append(str(6-i) + "  " + ' '.join(piece.rjust(3) for piece in row) + '\n')
        board_substrings.append('\n')
        board_substrings.append('     A   B   C   D   E')
        return ''.join(board_substrings)

    """
    Check if the move is valid    
    
    Args: 
        - game_state:   dictionary | Dictionary representing the current game state
        - move          tuple | the move which we check the validity of ((start_row, start_col),(end_row, end_col))
    Returns:
        - boolean representing the validity of the move
    """
    def is_valid_move(self, game_state, move):
        # Check if move is in list of valid moves
        return move in self.valid_moves(game_state)

    @staticmethod
    def is_valid_coordinate(coordinate: tuple[int, int]):
        indexed_row, indexed_col = coordinate
        return -1 < indexed_row < 5 and -1 < indexed_col < 5

    @staticmethod
    def print_valid_moves(moves, game_state):
        piece_translation = {
            "p": 'Pawn',
            "N": 'Knight',
            "B": 'Bishop',
            "Q": 'Queen',
            "K": 'King',
        }

        for move in moves:
            print(f'{piece_translation[game_state["board"][move[0][0]][move[0][1]][1]]} {MiniChess.get_readable_move(move)}')

    @staticmethod
    def get_readable_move(move):
        column_translation = {
            0: 'A',
            1: 'B',
            2: 'C',
            3: 'D',
            4: 'E',
        }
        return f'{column_translation[move[0][1]]}{5 - move[0][0]} {column_translation[move[1][1]]}{5 - move[1][0]}'

    """
    Returns a list of valid moves

    Args:
        - game_state:   dictionary | Dictionary representing the current game state
    Returns:
        - valid moves:   list | A list of nested tuples corresponding to valid moves [((start_row, start_col),(end_row, end_col)),((start_row, start_col),(end_row, end_col))]
    """
    def valid_moves(self, game_state):
        # Return a list of all the valid moves.
        # Implement basic move validation
        # Check for out-of-bounds, correct turn, move legality, etc
        moves = []
        for row_index, row in enumerate(game_state["board"]):
            for col_index, piece in enumerate(row):
                if piece[0] == game_state["turn"][0]:
                    if piece[1] == 'p':
                        # Can we go forward
                        end_row = row_index - 1 if game_state["turn"] == 'white' else row_index + 1
                        if (MiniChess.is_valid_coordinate((end_row, col_index)) and
                            game_state["board"][end_row][col_index] == '.'):
                            moves.append(((row_index, col_index), (end_row, col_index)))
                        # Can we capture diagonally
                        for column_direction in [-1, 1]:
                            diagonal_column = col_index + column_direction
                            if (MiniChess.is_valid_coordinate((end_row, diagonal_column)) and
                                game_state["board"][end_row][diagonal_column] != '.' and
                                game_state["board"][end_row][diagonal_column][0] != game_state["turn"][0]):
                                moves.append(((row_index, col_index), (end_row, diagonal_column)))
                    elif piece[1] == 'N':
                        directions = ((-1, -2), (-1, 2), (1, -2), (1, 2), (-2, -1), (-2, 1), (2, -1), (2, 1))
                        end_positions = [
                            (row_index + x, col_index + y) for x, y in directions
                            if MiniChess.is_valid_coordinate((row_index + x, col_index + y)) and
                            game_state["board"][row_index + x][col_index + y][0] != game_state["turn"][0]
                            ]
                        for knight_position in end_positions:
                            moves.append(((row_index, col_index), knight_position))
                    elif piece[1] == 'B':
                        unit_directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
                        for direction in unit_directions:
                            end_row = row_index + direction[0]
                            end_column = col_index + direction[1]
                            while (MiniChess.is_valid_coordinate((end_row, end_column)) and
                                game_state["board"][end_row][end_column][0] != game_state["turn"][0]):
                                moves.append(((row_index, col_index), (end_row, end_column)))
                                if game_state["board"][end_row][end_column] != '.':
                                    break
                                end_row = end_row + direction[0]
                                end_column = end_column + direction[1]
                    elif piece[1] == 'Q':
                        unit_directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
                        for direction in unit_directions:
                            end_row = row_index + direction[0]
                            end_column = col_index + direction[1]
                            while (MiniChess.is_valid_coordinate((end_row, end_column)) and
                                   game_state["board"][end_row][end_column][0] != game_state["turn"][0]):
                                moves.append(((row_index, col_index), (end_row, end_column)))
                                if game_state["board"][end_row][end_column] != '.':
                                    break
                                end_row = end_row + direction[0]
                                end_column = end_column + direction[1]
                    elif piece[1] == 'K':
                        directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
                        end_positions = [
                            (row_index + x, col_index + y) for x, y in directions
                            if MiniChess.is_valid_coordinate((row_index + x, col_index + y)) and
                               game_state["board"][row_index + x][col_index + y][0] != game_state["turn"][0]
                        ]
                        for king_position in end_positions:
                            moves.append(((row_index, col_index), king_position))
        return moves

    """
    Modify to board to make a move

    Args: 
        - game_state:   dictionary | Dictionary representing the current game state
        - move          tuple | the move to perform ((start_row, start_col),(end_row, end_col))
    Returns:
        - game_state:   dictionary | Dictionary representing the modified game state
    """
    def make_move(self, game_state, move):
        start = move[0]
        end = move[1]
        start_row, start_col = start
        end_row, end_col = end
        piece = game_state["board"][start_row][start_col]
        end_piece = game_state["board"][end_row][end_col]
        game_state["board"][start_row][start_col] = '.'
        game_state["board"][end_row][end_col] = piece
        if piece == 'wp' and end_row == 0:
            game_state["board"][end_row][end_col] = 'wQ'
        elif piece == 'bp' and end_row == 4:
            game_state["board"][end_row][end_col] = 'bQ'
        if piece[0] == 'w':
            if end_piece == '.':
                game_state["turn_no_capture"] = True
            else:
                game_state["turn_no_capture"] = False
                game_state["turns_without_capture"] = 0
        elif piece[0] == 'b':
            if end_piece != '.':
                game_state["turn_no_capture"] = False
                game_state["turns_without_capture"] = 0
            else:
                if game_state["turn_no_capture"]:
                    game_state["turns_without_capture"] += 1
        if end_piece in ['bK', 'wK']:
            game_state["game_over_reason"] = 'king captured'
            return game_state
        elif game_state["turn_number"] == self.max_turns and piece[0] == 'b':
            game_state["game_over_reason"] = 'max turns'
            return game_state
        elif game_state["turns_without_capture"] == 10:
            game_state["game_over_reason"] = 'no captures'
            return game_state
        game_state["turn_number"] = game_state["turn_number"] + 1 if piece[0] == 'b' else game_state["turn_number"]
        game_state["turn"] = "black" if game_state["turn"] == "white" else "white"
        return game_state

    """
    Parse the input string and modify it into board coordinates

    Args:
        - move: string representing a move "B2 B3"
    Returns:
        - (start, end)  tuple | the move to perform ((start_row, start_col),(end_row, end_col))
    """
    def parse_input(self, move):
        try:
            start, end = move.split()
            start = (5-int(start[1]), ord(start[0].upper()) - ord('A'))
            end = (5-int(end[1]), ord(end[0].upper()) - ord('A'))
            return (start, end)
        except:
            return None

    def minimax(self, game_state, depth, turn, start_time, is_max=True, alpha=-math.inf, beta=math.inf):
        self.total_nodes += 1
        self.states_visited_per_depth[self.depth - depth] += 1
        if depth == 0 or game_state["game_over_reason"] or (time.time() - start_time >= self.timeout - 0.01):
            return self.heuristic(game_state, turn), None
        self.non_leaf_nodes += 1
        if is_max:
            maximum = -math.inf
            potential_moves = self.valid_moves(game_state)
            best_move = None
            for move in potential_moves:
                potential_state = self.make_move(copy.deepcopy(game_state), move)
                state_value, _ = self.minimax(potential_state, depth - 1, turn, start_time, False, alpha, beta)
                if state_value > maximum:
                    maximum = state_value
                    best_move = move
                if self.alphabeta:
                    alpha = max(alpha, state_value)
                    if beta <= alpha:
                        break
            return maximum, best_move
        else:
            minimum = math.inf
            potential_moves = self.valid_moves(game_state)
            best_move = None
            for move in potential_moves:
                potential_state = self.make_move(copy.deepcopy(game_state), move)
                state_value, _ = self.minimax(potential_state, depth - 1, turn, start_time,True, alpha, beta)
                if state_value < minimum:
                    minimum = state_value
                    best_move = move
                if self.alphabeta:
                    beta = min(beta, state_value)
                    if beta <= alpha:
                        break
            return minimum, best_move

    """
    Game loop

    Args:
        - None
    Returns:
        - None
    """
    def play(self):
        with open(f'gameTrace-{self.alphabeta}-{self.timeout}-{self.max_turns}.txt', 'w') as file:
            self.log_parameters(file)
            if self.max_turns <= 0:
                print('Invalid amount of turns. Exiting program.')
                file.write('Invalid amount of turns. Exiting program.')
                exit(2)
            print("Welcome to Mini Chess! Enter moves as 'B2 B3'. Type 'exit' to quit.")
            while not self.current_game_state["game_over_reason"]:
                print(f'\nTurn #{self.current_game_state["turn_number"]}')
                file.write(f'\nTurn #{self.current_game_state["turn_number"]}\n')
                board = MiniChess.get_formatted_board(self.current_game_state)
                print(board)
                file.write(f'{board}\n')
                if ((self.current_game_state["turn"] == 'white' and self.white_ai) or
                    (self.current_game_state["turn"] == 'black' and self.black_ai)):
                    current_time = time.time()
                    minimax_score, move = self.minimax(self.current_game_state, self.depth, self.current_game_state["turn"], current_time)
                    total_time = time.time() - current_time
                    print(f'Heuristic score: {self.heuristic(self.current_game_state, self.current_game_state["turn"])}')
                    file.write(f'Heuristic score: {self.heuristic(self.current_game_state, self.current_game_state["turn"])}\n')
                    print(f"{self.current_game_state["turn"].capitalize()} to move: {MiniChess.get_readable_move(move)}")
                    file.write(f"{self.current_game_state["turn"].capitalize()} to move: {MiniChess.get_readable_move(move)}\n")
                    self.make_move(self.current_game_state, move)
                    print(f'Time taken to compute move: {total_time}s')
                    file.write(f'Time taken to compute move: {total_time}s\n')
                    print(f'Minimax search score: {minimax_score}')
                    file.write(f'Minimax search score: {minimax_score}\n')
                    cumulative_states_visited = sum(self.states_visited_per_depth)
                    print(f'Cumulative states explored: {cumulative_states_visited}')
                    file.write(f'Cumulative states explored: {cumulative_states_visited}\n')
                    print(f'Cumulative states explored per depth: {self.states_visited_per_depth}')
                    file.write(f'Cumulative states explored per depth: {self.states_visited_per_depth}\n')
                    print(f'Cumulative % states explored per depth: {[a / cumulative_states_visited for a in self.states_visited_per_depth]}')
                    file.write(f'Cumulative % states explored per depth: {[a / cumulative_states_visited for a in self.states_visited_per_depth]}\n')
                    print(f'Branching factor: {(self.total_nodes - 1) / self.non_leaf_nodes}')
                    self.total_nodes = self.non_leaf_nodes = 0
                else:
                    move = input(f"{self.current_game_state['turn'].capitalize()} to move: ")
                    file.write(f"{self.current_game_state['turn'].capitalize()} to move: {move}\n")
                    if move.lower() == 'exit':
                        print("\nGame exited.")
                        file.write('\nGame exited.')
                        exit(1)
                    move = self.parse_input(move)
                    if not move or not self.is_valid_move(self.current_game_state, move):
                        print("Invalid move. Try again.")
                        file.write('Invalid move. Try again.\n')
                        continue
                    self.make_move(self.current_game_state, move)

            # If we reach here, the game is over
            board = MiniChess.get_formatted_board(self.current_game_state)
            print()
            print(board)
            file.write('\n')
            file.write(board)
            if self.current_game_state["game_over_reason"] == 'king captured':
                print(f"\n{self.current_game_state['turn'].capitalize()} WINS in {self.current_game_state["turn_number"]} turns!")
                file.write(f"\n{self.current_game_state['turn'].capitalize()} WINS in {self.current_game_state["turn_number"]} turns!")
            elif self.current_game_state["game_over_reason"] == 'max turns':
                print('\nMaximum amount of turns reached, DRAW')
                file.write('\nMaximum amount of turns reached, DRAW')
            else:
                print('\nThere has been no captures in 10 turns, DRAW')
                file.write('\nThere has been no captures in 10 turns, DRAW')
                
    def log_parameters(self, file):
        file.write(f'Max turns: {self.max_turns}\n')
        file.write(f'{'Human' if not self.white_ai else 'AI'} vs. {'Human' if not self.black_ai else 'AI'}\n')
        if self.white_ai or self.black_ai:
            file.write(f'alphabeta: {'enabled' if self.alphabeta else 'disabled'}\n')
            file.write(f'Heuristic: {self.heuristic.__name__}\n')
            file.write(f'Timeout: {self.timeout}s\n')

    def set_parameters(self):
        max_turns = int(input('Enter the maximum amount of turns: '))
        white_ai = True if input('Is white an AI? (Y/N): ').lower() == 'y' else False
        black_ai = True if input('Is black an AI? (Y/N): ').lower() == 'y' else False
        timeout = None
        alphabeta = None
        heuristic = None
        depth = None
        if white_ai or black_ai:
            timeout = int(input('Enter the timeout in seconds: '))
            alphabeta = True if input('Do you want to enable alphabeta? (Y/N): ').lower() == 'y' else False
            heuristic = self.select_heuristic(input('Which heuristic do you want to use? (e0, e1, e2): ').lower())
            depth = int(input('Enter the search depth: '))
        return timeout, max_turns, white_ai, black_ai, alphabeta, heuristic, depth

    def set_stats(self):
        states_visited_per_depth, non_leaf_nodes, total_nodes = None, None, None
        if self.white_ai or self.black_ai:
            states_visited_per_depth = [0 for _ in range(self.depth + 1)]
            non_leaf_nodes = 0
            total_nodes = 0
        return states_visited_per_depth, non_leaf_nodes, total_nodes

    def king_safety_score(self, game_state, turn):
        king_coordinate = None
        for row_index, row in enumerate(game_state["board"]):
            for col_index, piece in enumerate(row):
                if piece == f'{turn[0]}K':
                    king_coordinate = (row_index, col_index)
        if king_coordinate is None:
            return -999
        if game_state["turn"] != turn:
            valid_moves = self.valid_moves(game_state)
            for _, end_pos in valid_moves:
                if king_coordinate == end_pos:
                    return -999
        if turn == 'white':
            forward_row = king_coordinate[0] - 1
            forward_pieces = 0
            for row in range(forward_row, -1, -1):
                for piece in game_state["board"][row]:
                    if piece[0] == 'w':
                        forward_pieces += 1
            return 4 * forward_pieces - 10
        else:
            forward_row = king_coordinate[0] + 1
            forward_pieces = 0
            for row in range(forward_row, 5, 1):
                for piece in game_state["board"][row]:
                    if piece[0] == 'b':
                        forward_pieces += 1
            return 4 * forward_pieces - 10

    @staticmethod
    def material_score(game_state):
        white_score, black_score = 0, 0
        piece_values = {
            "p": 1,
            "B": 3,
            "N": 3,
            "Q": 9,
            "K": 999
        }
        for row in game_state["board"]:
            for piece in row:
                if piece[0] == 'w':
                    white_score += piece_values[piece[1]]
                elif piece[0] == 'b':
                    black_score += piece_values[piece[1]]
        return white_score - black_score

    def select_heuristic(self, heuristic_input):
        def e0(game_state, _):
            return MiniChess.material_score(game_state)

        def e1(game_state, turn):
            score = 0
            score += self.king_safety_score(game_state, turn)
            material_score = MiniChess.material_score(game_state) if turn == 'white' else -MiniChess.material_score(game_state)
            score += material_score
            return score

        def e2(game_state, turn):
            w_center_pieces, b_center_pieces = 0, 0
            for i in range(1, 4, 1):
                for j in range(1, 4, 1):
                    if game_state["board"][i][j][0] == 'w':
                        w_center_pieces += 1
                    elif game_state["board"][i][j][0] == 'b':
                        b_center_pieces += 1
            return w_center_pieces - b_center_pieces if turn == 'white' else b_center_pieces - w_center_pieces

        if heuristic_input == 'e1':
            return e1
        elif heuristic_input == 'e2':
            return e2
        else:
            return e0

if __name__ == "__main__":
    game = MiniChess()
    game.play()