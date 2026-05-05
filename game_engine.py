"""
Connect 4 Game Engine
====================
Handles all game logic: board state, move validation, win detection.
Student 1 responsibility: Game Engine
"""

import numpy as np
from typing import Optional, List, Tuple

ROWS = 6
COLS = 7
EMPTY = 0
PLAYER = 1
AI = 2

WINDOW_LENGTH = 4


class GameEngine:
    def __init__(self):
        self.board = np.zeros((ROWS, COLS), dtype=int)
        self.game_over = False
        self.turn = PLAYER  # Player goes first

    def reset(self):
        self.board = np.zeros((ROWS, COLS), dtype=int)
        self.game_over = False
        self.turn = PLAYER

    def is_valid_location(self, col: int) -> bool:
        """Check if a column has space for another piece."""
        return 0 <= col < COLS and self.board[0][col] == EMPTY

    def get_valid_locations(self) -> List[int]:
        """Return list of columns that can accept a piece."""
        return [col for col in range(COLS) if self.is_valid_location(col)]

    def get_next_open_row(self, col: int) -> int:
        """Find the lowest empty row in a column (gravity simulation)."""
        for row in range(ROWS - 1, -1, -1):
            if self.board[row][col] == EMPTY:
                return row
        return -1  # Column is full

    def drop_piece(self, col: int, piece: int) -> int:
        """Drop a piece into the column. Returns the row it landed on."""
        row = self.get_next_open_row(col)
        if row != -1:
            self.board[row][col] = piece
        return row

    def undo_piece(self, col: int) -> None:
        """Remove the top piece from a column (used by AI search)."""
        for row in range(ROWS):
            if self.board[row][col] != EMPTY:
                self.board[row][col] = EMPTY
                return

    def check_win(self, piece: int) -> bool:
        """Check if the given piece has won the game."""
        # Horizontal
        for row in range(ROWS):
            for col in range(COLS - 3):
                if all(self.board[row][col + i] == piece for i in range(4)):
                    return True

        # Vertical
        for row in range(ROWS - 3):
            for col in range(COLS):
                if all(self.board[row + i][col] == piece for i in range(4)):
                    return True

        # Diagonal (positive slope)
        for row in range(ROWS - 3):
            for col in range(COLS - 3):
                if all(self.board[row + i][col + i] == piece for i in range(4)):
                    return True

        # Diagonal (negative slope)
        for row in range(3, ROWS):
            for col in range(COLS - 3):
                if all(self.board[row - i][col + i] == piece for i in range(4)):
                    return True

        return False

    def get_winning_cells(self, piece: int) -> Optional[List[Tuple[int, int]]]:
        """Return the coordinates of the winning 4 cells, or None."""
        # Horizontal
        for row in range(ROWS):
            for col in range(COLS - 3):
                cells = [(row, col + i) for i in range(4)]
                if all(self.board[r][c] == piece for r, c in cells):
                    return cells

        # Vertical
        for row in range(ROWS - 3):
            for col in range(COLS):
                cells = [(row + i, col) for i in range(4)]
                if all(self.board[r][c] == piece for r, c in cells):
                    return cells

        # Diagonal (positive slope)
        for row in range(ROWS - 3):
            for col in range(COLS - 3):
                cells = [(row + i, col + i) for i in range(4)]
                if all(self.board[r][c] == piece for r, c in cells):
                    return cells

        # Diagonal (negative slope)
        for row in range(3, ROWS):
            for col in range(COLS - 3):
                cells = [(row - i, col + i) for i in range(4)]
                if all(self.board[r][c] == piece for r, c in cells):
                    return cells

        return None

    def is_terminal_node(self) -> bool:
        """Check if the game has ended (win or draw)."""
        return (
            self.check_win(PLAYER)
            or self.check_win(AI)
            or len(self.get_valid_locations()) == 0
        )

    def is_draw(self) -> bool:
        """Check if the board is full with no winner."""
        return len(self.get_valid_locations()) == 0 and not self.check_win(PLAYER) and not self.check_win(AI)

    def get_board_copy(self) -> np.ndarray:
        return self.board.copy()
