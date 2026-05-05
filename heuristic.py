# We played around with these numbers. 
# At first, the AI was too aggressive and kept losing,
# so we boosted the "opp_three_block" weight to -80 so it actually blocks the player.

import numpy as np
from game_engine import ROWS, COLS, EMPTY, PLAYER, AI, WINDOW_LENGTH


# We changed this from 40 to 80 because the AI was letting the player win too easily on 3-in-a-rows.
WEIGHTS = {
    "four_in_a_row":    1_000_000,   # Immediate win
    "three_in_a_row":   50,          # Three with one open space
    "two_in_a_row":     10,          # Two with two open spaces
    "center_control":   6,           # Bonus for center column placement
    "opp_three_block":  -80,         # Penalize letting opponent get 3
    "opp_two_block":    -5,          # Penalize letting opponent get 2
}


def score_window(window: list, piece: int, weights: dict) -> int:
    #Score a window of 4 cells from the AI's perspective.
    # This part is basically the 'brain' of the scoring system.
    score = 0
    opp_piece = PLAYER if piece == AI else AI

    piece_count = window.count(piece)
    empty_count = window.count(EMPTY)
    opp_count = window.count(opp_piece)

    if piece_count == 4:
        score += weights["four_in_a_row"]
    elif piece_count == 3 and empty_count == 1:
        score += weights["three_in_a_row"]
    elif piece_count == 2 and empty_count == 2:
        score += weights["two_in_a_row"]

    # Penalize opponent threats
    if opp_count == 3 and empty_count == 1:
        score += weights["opp_three_block"]
    elif opp_count == 2 and empty_count == 2:
        score += weights["opp_two_block"]

    return score

# Note: We checked, and center control really is the key to winning mid-game.
def score_board(board: np.ndarray, piece: int, weights: dict = None) -> int:
    
    if weights is None:
        weights = WEIGHTS

    score = 0

    #Center Column Preference
    # The middle column is the most important for making 4-in-a-row, so we give it a small bonus.
    center_array = [int(board[row][COLS // 2]) for row in range(ROWS)]
    center_count = center_array.count(piece)
    score += center_count * weights["center_control"]

    #Horizontal Windows
    for row in range(ROWS):
        row_array = [int(board[row][col]) for col in range(COLS)]
        for col in range(COLS - 3):
            window = row_array[col:col + WINDOW_LENGTH]
            score += score_window(window, piece, weights)

    #Vertical Windows
    for col in range(COLS):
        col_array = [int(board[row][col]) for row in range(ROWS)]
        for row in range(ROWS - 3):
            window = col_array[row:row + WINDOW_LENGTH]
            score += score_window(window, piece, weights)

    # Check diagonals going up /
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            window = [board[row + i][col + i] for i in range(WINDOW_LENGTH)]
            score += score_window(window, piece, weights)

    # Check diagonals going down \
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            window = [board[row - i][col + i] for i in range(WINDOW_LENGTH)]
            score += score_window(window, piece, weights)

    return score


#Alternative Heuristic Presets for Research Comparison 
AGGRESSIVE_WEIGHTS = {
    "four_in_a_row":    1_000_000,
    "three_in_a_row":   100,       # Much higher offensive bias
    "two_in_a_row":     20,
    "center_control":   3,
    "opp_three_block":  -50,       # Less defensive
    "opp_two_block":    -2,
}

DEFENSIVE_WEIGHTS = {
    "four_in_a_row":    1_000_000,
    "three_in_a_row":   20,        # Less offensive
    "two_in_a_row":     5,
    "center_control":   4,
    "opp_three_block":  -150,      # Much more defensive
    "opp_two_block":    -15,
}

CENTER_HEAVY_WEIGHTS = {
    "four_in_a_row":    1_000_000,
    "three_in_a_row":   50,
    "two_in_a_row":     10,
    "center_control":   20,        # Extreme center bias
    "opp_three_block":  -80,
    "opp_two_block":    -5,
}

HEURISTIC_PRESETS = {
    "Balanced (Default)": WEIGHTS,
    "Aggressive":         AGGRESSIVE_WEIGHTS,
    "Defensive":          DEFENSIVE_WEIGHTS,
    "Center-Heavy":       CENTER_HEAVY_WEIGHTS,
}
