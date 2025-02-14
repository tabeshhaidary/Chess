import math
import copy
import time
import argparse

class MiniChess:
    
    def __init__(self):
        self.current_game_state = self.init_board()
        self.game_over = False
        self.total_moves = 0
        self.turns = 1
        self.moves_without_capture = 0
        (self.timeout,
        self.max_turns,
        self.p1_ai,
        self.p2_ai,
        self.alphabeta,
        self.heuristic) = self.set_parameters()

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
        
    def get_formatted_board(self, game_state):
        board_substrings = []
        board_substrings.append('\n')
        for i, row in enumerate(game_state["board"], start=1):
            board_substrings.append(str(6-i) + "  " + ' '.join(piece.rjust(3) for piece in row) + '\n')
        board_substrings.append('\n')
        board_substrings.append('     A   B   C   D   E\n')
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
        column_translation = {
            0: 'A',
            1: 'B',
            2: 'C',
            3: 'D',
            4: 'E',
        }
        for move in moves:
            print((f'{piece_translation[game_state["board"][move[0][0]][move[0][1]][1]]} '
                                     f'{column_translation[move[0][1]]}{5 - move[0][0]} to '
                                     f'{column_translation[move[1][1]]}{5 - move[1][0]}'))

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
        self.total_moves += 1
        self.moves_without_capture = self.moves_without_capture + 1 if end_piece == '.' else 0
        if end_piece in ['bK', 'wK'] or self.moves_without_capture == 20:
            self.game_over = True
            return game_state
        if piece[0] == 'b':
            self.turns += 1
        if self.turns > self.max_turns:
            self.game_over = True
            return game_state
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
            if (self.max_turns == 0):
                print('Maximum amount of turns is 0. Exiting program.')
                file.write('Maximum amount of turns is 0. Exiting program.')
                exit(2)
            print("Welcome to Mini Chess! Enter moves as 'B2 B3'. Type 'exit' to quit.")
            board = None
            while not self.game_over:
                file.write(f'\nTurn #{self.turns}')
                board = self.get_formatted_board(self.current_game_state)
                print(board)
                file.write(f'{board}\n')
                #MiniChess.print_valid_moves(self.valid_moves(self.current_game_state), self.current_game_state)
                move = input(f"{self.current_game_state['turn'].capitalize()} to move: ")
                file.write(f"{self.current_game_state['turn'].capitalize()} to move: {move}\n")
                if move.lower() == 'exit':
                    print("\nGame exited.")
                    file.write('\nGame exited.')
                    exit(1)

                move = self.parse_input(move)
                if not move or not self.is_valid_move(self.current_game_state, move):
                    print("Invalid move. Try again.")
                    file.write('Invalid move. Try again.')
                    continue

                self.make_move(self.current_game_state, move)

            # If we reach here, the game is over
            board = self.get_formatted_board(self.current_game_state)
            print(board)
            file.write(board)
            if self.moves_without_capture >= 20:
                print('\nThere has been no captures in 10 turns, DRAW')
                file.write('\nThere has been no captures in 10 turns, DRAW')
            elif self.turns >= self.max_turns:
                print('\nMaximum amount of turns reached, DRAW')
                file.write('\nMaximum amount of turns reached, DRAW')
            else:
                print(f"\n{self.current_game_state['turn'].capitalize()} WINS in {self.turns} turns!")
                file.write(f"\n{self.current_game_state['turn'].capitalize()} WINS in {self.turns} turns!")
                
    def log_parameters(self, file):
        file.write(f'Max turns: {self.max_turns}\n')
        file.write(f'{'Human' if self.p1_ai == 'n' else 'AI'} vs. {'Human' if self.p2_ai == 'n' else 'AI'}\n')
        if self.p1_ai == 'y' or self.p2_ai == 'y':
            file.write(f'alphabeta: {'enabled' if self.alphabeta == 'y' else 'disabled'}\n')
            file.write(f'Heuristic: {self.heuristic}\n')
            file.write(f'Timeout: {self.timeout}s\n')
            
    def set_parameters(self):
        max_turns = int(input('Enter the maximum amount of turns: '))
        p1_ai = input('Is player 1 an AI? (Y/N): ').lower()
        p2_ai = input('Is player 2 an AI? (Y/N): ').lower()
        timeout = False
        alphabeta = False
        heuristic = ''
        if p1_ai == 'y' or p2_ai == 'y':
            timeout = int(input('Enter the timeout in seconds: '))
            alphabeta = input('Do you want to enable alphabeta? (Y/N): ').lower()
            heuristic = input('Which heuristic do you want to use? (e0, e1, e2): ').lower()
        return timeout, max_turns, p1_ai, p2_ai, alphabeta, heuristic
            
if __name__ == "__main__":
    game = MiniChess()
    game.play()
