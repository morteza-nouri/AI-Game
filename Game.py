from random import random, choice
import copy
import math
import numpy as np
import time


class ConnectSin:
    YOU = 1
    CPU = -1
    EMPTY = 0
    DRAW = 0
    __CONNECT_NUMBER = 4
    board = None

    def __init__(self, board_size=(6, 7), silent=False):
        """
        The main class for the connect4 game

        Inputs
        ----------
        board_size : a tuple representing the board size in format: (rows, columns)
        silent     : whether the game prints outputs or not
        """
        assert len(board_size) == 2, "board size should be a 1*2 tuple"
        assert board_size[0] > 4 and board_size[1] > 4, "board size should be at least 5*5"

        self.columns = board_size[1]
        self.rows = board_size[0]
        self.silent = silent
        self.board_size = self.rows * self.columns
        self.explored = 0

    def run(self, starter=None):
        """
        runs the game!

        Inputs
        ----------
        starter : either -1,1 or None. -1 if cpu starts the game, 1 if you start the game. None if you want the starter
            to be assigned randomly

        Output
        ----------
        (int) either 1,0,-1. 1 meaning you have won, -1 meaning the player has won and 0 means that the game has drawn
        """
        if (not starter):
            starter = self.__get_random_starter()
        assert starter in [
            self.YOU, self.CPU], "starter value can only be 1,-1 or None"

        self.__init_board()
        turns_played = 0
        current_player = starter
        while(turns_played < self.board_size):

            if (current_player == self.YOU):
                self.__print_board()
                player_input = self.get_your_input()
            elif (current_player == self.CPU):
                player_input = self.__get_cpu_input()
            else:
                raise Exception(
                    "A problem has happend! contact no one, there is no fix!")
            if (not self.register_input(player_input, current_player)):
                self.__print("this move is invalid!")
                continue
            current_player = self.__change_turn(current_player)
            potential_winner = self.check_for_winners()
            turns_played += 1
            if (potential_winner != 0):
                self.__print_board()
                self.__print_winner_message(potential_winner)
                return potential_winner
        self.__print_board()
        self.__print("The game has ended in a draw!")
        return self.DRAW

    def evaluation(self):
        """
        evaluate score of current board state, this method traverse in 4 direction and find 2-consecutive and 3-consecutive 
        YOU pieces and CPU pieces and then increment the score.
        
        Outputs
        ----------
        returns the score of current board state
        """
        score = 0
        score += self.__horizontal_score(self.__CONNECT_NUMBER - 2)
        score += self.__horizontal_score(self.__CONNECT_NUMBER - 1)
        score += self.__vertical_score(self.__CONNECT_NUMBER - 2)
        score += self.__vertical_score(self.__CONNECT_NUMBER - 1)
        score += self.__diagonal_up_score(self.__CONNECT_NUMBER - 2)
        score += self.__diagonal_up_score(self.__CONNECT_NUMBER - 1)
        score += self.__diagonal_down_score(self.__CONNECT_NUMBER - 2)
        score += self.__diagonal_down_score(self.__CONNECT_NUMBER - 1)
        return score

    def __horizontal_score(self, consecSlice):
        """
        Traverse horizontally to find consecSlice-consecutive pieces of YOU and CPU and increments for YOU pieces
        and decrements for CPU pieces.
        
        Inputs
        -------
        consecutive slice to consider in traversing
        
        Output
        --------
        horizontal evaluation score of board state
        """
        score = 0
        for i in range(self.rows):
            for j in range(self.columns - consecSlice + 1):
                win = self.board[i][j:j+consecSlice]
                if win == [self.YOU] * 3:
                    score += 45
                elif win == [self.CPU] * 3:
                    score -= 45
                elif win == [self.YOU] * 2:
                    score += 4
                elif win == [self.CPU] * 2:
                    score -= 4
                else: pass
        return score

    def __vertical_score(self, consecSlice):
        score = 0
        board = np.array(self.board)
        for j in range(self.columns):
            col_array = [int(x) for x in list(board[:,j])]
            for i in range(self.rows - consecSlice + 1):
                win = col_array[i:i+consecSlice]
                if win == [self.YOU] * 3:
                    score += 45
                elif win == [self.CPU] * 3:
                    score -= 45
                elif win == [self.YOU] * 2:
                    score += 4
                elif win == [self.CPU] * 2:
                    score -= 4
                else:
                    pass
        return score 

    def __diagonal_up_score(self, consecSlice):
        score = 0
        for r in range(self.rows - consecSlice):
            for c in range(self.columns - consecSlice):
                win = [self.board[r+i][c+i] for i in range(consecSlice)]
                if win == [self.YOU] * 3:
                    score += 45
                elif win == [self.CPU] * 3:
                    score -= 45
                elif win == [self.YOU] * 2:
                    score += 4
                elif win == [self.CPU] * 2:
                    score -= 4
                else:
                    pass
        return score 
    
    def __diagonal_down_score(self, consecSlice):
        score = 0
        for r in range(self.rows - consecSlice):
            for c in range(self.columns - consecSlice):
                win = [self.board[r+consecSlice-i][c+i] for i in range(consecSlice)]
                if win == [self.YOU] * 3:
                    score += 45
                elif win == [self.CPU] * 3:
                    score -= 45
                elif win == [self.YOU] * 2:
                    score += 4
                elif win == [self.CPU] * 2:
                    score -= 4
                else:
                    pass
        return score 


    def minimax(self, depth, turn):
        self.explored += 1
        pm = self.get_possible_moves()
        score = 0
        if depth == 0 or self.check_if_player_has_won(self.YOU) or self.check_if_player_has_won(self.CPU) or len(pm) == 0:
            if self.check_if_player_has_won(self.YOU) or self.check_if_player_has_won(self.CPU) or len(pm) == 0:
                if self.check_if_player_has_won(self.YOU):
                    score += 1000000
                elif self.check_if_player_has_won(self.CPU):
                    score -= 1000000
                else:
                    score += self.evaluation()
            else:
                score += self.evaluation()

            return None, score

        boardCpy = copy.deepcopy(self.board)
        if turn == self.YOU:  # Maximizer
            bestValue = float('-inf')
            column = choice(pm)
            for m in pm:
                if self.is_move_valid(m):
                    self.register_input(m, self.YOU)
                    value = self.minimax(depth-1, self.CPU)[1]
                    if value > bestValue:
                        column = m
                        bestValue = value
                self.board = copy.deepcopy(boardCpy)
            return column, bestValue

        else:  # turn == self.CPU, Minimizer
            bestValue = float('inf')
            column = choice(pm)
            for m in pm:
                if self.is_move_valid(m):
                    self.register_input(m, self.CPU)
                    value = self.minimax(depth-1, self.YOU)[1]
                    if value < bestValue:
                        column = m
                        bestValue = value
                self.board = copy.deepcopy(boardCpy)
            return column, bestValue

    def minimaxAlphaBeta(self, depth, turn, alpha = float('-inf'), beta = float('inf')):
        self.explored += 1
        pm = self.get_possible_moves()
        score = 0
        if depth == 0 or self.check_if_player_has_won(self.YOU) or self.check_if_player_has_won(self.CPU) or len(pm) == 0:
            if self.check_if_player_has_won(self.YOU) or self.check_if_player_has_won(self.CPU) or len(pm) == 0:
                if self.check_if_player_has_won(self.YOU):
                    score += 1000000
                elif self.check_if_player_has_won(self.CPU):
                    score -= 1000000
                else:
                    score += self.evaluation()
            else:
                score += self.evaluation()

            return None, score

        boardCpy = copy.deepcopy(self.board)
        if turn == self.YOU:  # Maximizer
            bestValue = float('-inf')
            column = choice(pm)
            for m in pm:
                if self.is_move_valid(m):
                    self.register_input(m, self.YOU)
                    value = self.minimaxAlphaBeta(depth-1, self.CPU, alpha, beta)[1]
                    if value > bestValue:
                        column = m
                        bestValue = value
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        beta
                self.board = copy.deepcopy(boardCpy)
            return column, bestValue

        else:  # turn == self.CPU, Minimizer
            bestValue = float('inf')
            column = choice(pm)
            for m in pm:
                if self.is_move_valid(m):
                    self.register_input(m, self.CPU)
                    value = self.minimaxAlphaBeta(depth-1, self.YOU, alpha, beta)[1]
                    if value < bestValue:
                        column = m
                        bestValue = value
                    beta = min(beta, value)
                    if beta <= alpha:
                        break
                self.board = copy.deepcopy(boardCpy)
            return column, bestValue

    def get_your_input(self):
        """
        gets your input

        Output
        ----------
        (int) an integer between 1 and column count. the column to put a piece in
        """
        col, val = self.minimaxAlphaBeta(7, self.YOU)
        print(f'explored states: {self.explored}')
        return col
        raise NotImplementedError

    def check_for_winners(self):
        """
        checks if anyone has won in this position

        Output
        ----------
        (int) either 1,0,-1. 1 meaning you have won, -1 meaning the player has won and 0 means that nothing has happened
        """
        have_you_won = self.check_if_player_has_won(self.YOU)
        if have_you_won:
            return self.YOU
        has_cpu_won = self.check_if_player_has_won(self.CPU)
        if has_cpu_won:
            return self.CPU
        return self.EMPTY

    def check_if_player_has_won(self, player_id):
        """
        checks if player with player_id has won

        Inputs
        ----------
        player_id : the id for the player to check

        Output
        ----------
        (boolean) true if the player has won in this position
        """
        return (
            self.__has_player_won_diagonally(player_id)
            or self.__has_player_won_horizentally(player_id)
            or self.__has_player_won_vertically(player_id)
        )

    def is_move_valid(self, move):
        """
        checks if this move can be played

        Inputs
        ----------
        move : the column to place a piece in, in range [1, column count]

        Output
        ----------
        (boolean) true if the move can be played
        """
        if (move < 1 or move > self.columns):
            return False
        column_index = move - 1
        return self.board[0][column_index] == 0

    def get_possible_moves(self):
        """
        returns a list of possible moves for the next move

        Output
        ----------
        (list) a list of numbers of columns that a piece can be placed in
        """
        possible_moves = []
        for i in range(self.columns):
            move = i + 1
            if (self.is_move_valid(move)):
                possible_moves.append(move)
        return possible_moves

    def register_input(self, player_input, current_player):
        """
        registers move to board, remember that this function changes the board

        Inputs
        ----------
        player_input : the column to place a piece in, in range [1, column count]
        current_player: ID of the current player, either self.YOU or self.CPU

        """
        if (not self.is_move_valid(player_input)):
            return False
        self.__drop_piece_in_column(player_input, current_player)
        return True

    def __init_board(self):
        self.board = []
        for i in range(self.rows):
            self.board.append([self.EMPTY] * self.columns)

    def __print(self, message: str):
        if not self.silent:
            print(message)

    def __has_player_won_horizentally(self, player_id):
        for i in range(self.rows):
            for j in range(self.columns - self.__CONNECT_NUMBER + 1):
                has_won = True
                for x in range(self.__CONNECT_NUMBER):
                    if self.board[i][j + x] != player_id:
                        has_won = False
                        break
                if has_won:
                    return True
        return False

    def __has_player_won_vertically(self, player_id):
        for i in range(self.rows - self.__CONNECT_NUMBER + 1):
            for j in range(self.columns):
                has_won = True
                for x in range(self.__CONNECT_NUMBER):
                    if self.board[i + x][j] != player_id:
                        has_won = False
                        break
                if has_won:
                    return True
        return False

    def __has_player_won_diagonally(self, player_id):
        for i in range(self.rows - self.__CONNECT_NUMBER + 1):
            for j in range(self.columns - self.__CONNECT_NUMBER + 1):
                has_won = True
                for x in range(self.__CONNECT_NUMBER):
                    if self.board[i + x][j + x] != player_id:
                        has_won = False
                        break
                if has_won:
                    return True
                has_won = True
                for x in range(self.__CONNECT_NUMBER):
                    if self.board[i + self.__CONNECT_NUMBER - 1 - x][j + x] != player_id:
                        has_won = False
                        break
                if has_won:
                    return True
        return False

    def __get_random_starter(self):
        players = [self.YOU, self.CPU]
        return players[int(random() * len(players))]

    def __get_cpu_input(self):
        """
        This is where clean code goes to die.
        """
        bb = copy.deepcopy(self.board)
        pm = self.get_possible_moves()
        for m in pm:
            self.register_input(m, self.CPU)
            if (self.check_if_player_has_won(self.CPU)):
                self.board = bb
                return m
            self.board = copy.deepcopy(bb)
        if (self.is_move_valid((self.columns // 2) + 1)):
            c = 0
            cl = (self.columns // 2) + 1
            for x in range(self.rows):
                if (self.board[x][cl] == self.CPU):
                    c += 1
            if (random() < 0.65):
                return cl
        return pm[int(random() * len(pm))]

    def __drop_piece_in_column(self, move, current_player):
        last_empty_space = 0
        column_index = move - 1
        for i in range(self.rows):
            if (self.board[i][column_index] == 0):
                last_empty_space = i
        self.board[last_empty_space][column_index] = current_player
        return True

    def __print_winner_message(self, winner):
        if (winner == self.YOU):
            self.__print("congrats! you have won!")
        else:
            self.__print("gg. CPU has won!")

    def __change_turn(self, turn):
        if (turn == self.YOU):
            return self.CPU
        else:
            return self.YOU

    def __print_board(self):
        if (self.silent):
            return
        print("Y: you, C: CPU")
        for i in range(self.rows):
            for j in range(self.columns):
                house_char = "O"
                if (self.board[i][j] == self.YOU):
                    house_char = "Y"
                elif (self.board[i][j] == self.CPU):
                    house_char = "C"

                print(f"{house_char}", end=" ")
            print()


board_sizes_to_check = [(6, 7),
                        (7, 8),
                        (7, 10)]
game = ConnectSin(board_size=(7, 10), silent=True)

res = 0
start = time.time()
for i in range(1):
    if game.run() == 1:
        res += 1

print(f"time spent: {time.time()-start}")
print(res)
