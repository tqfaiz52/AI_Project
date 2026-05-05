
import math
from game_engine import GameEngine, PLAYER, AI, ROWS, COLS
from heuristic import score_board, WEIGHTS


class AIAgent:
    def __init__(self, depth: int = 5, use_alpha_beta: bool = True, weights: dict = None):
    
        self.depth = depth
        self.use_alpha_beta = use_alpha_beta
        self.weights = weights if weights else WEIGHTS
        self.nodes_expanded = 0   # We use this to compare Minimax vs Alpha-Beta performance

    def reset_node_count(self):
        self.nodes_expanded = 0

    def get_move(self, engine: GameEngine) -> tuple[int, int]:
        # Find the best move for AI. Returns (best_col, nodes_expanded).
    
        self.reset_node_count()

        if self.use_alpha_beta:
            _, col = self._minimax_ab(
                engine.board.copy(), self.depth,
                -math.inf, math.inf, True
            )
        else:
            _, col = self._minimax(engine.board.copy(), self.depth, True)

        return col, self.nodes_expanded

    #Pure Minimax (No Pruning)

    def _minimax(self, board, depth: int, maximizing: bool) -> tuple[int, int]:

        # We have to copy the board so we don't mess up the actual game state during search.
        temp = GameEngine()
        temp.board = board

        valid_locations = temp.get_valid_locations()
        gameover = temp.is_terminal_node()

        #Base Cases
        if is_terminal:
            self.nodes_expanded += 1
            if temp.check_win(AI):
                return (10_000_000 + depth, None)   # AI wins (prefer faster wins)
            elif temp.check_win(PLAYER):
                return (-10_000_000 - depth, None)  # Human wins
            else:
                return (0, None)                    # Draw

        if depth == 0:
            self.nodes_expanded += 1
            return (score_board(board, AI, self.weights), None)

        #Recursive Cases
        if maximizing:
            best_score = -99999999
            best_col = valid_locations[len(valid_locations) // 2]  # Prefer center

            for col in self._order_moves(valid_locations):
                self.nodes_expanded += 1
                temp2 = GameEngine()
                temp2.board = board.copy()
                temp2.drop_piece(col, AI)
                new_score, _ = self._minimax(temp2.board, depth - 1, False)
                if new_score > value:
                    value = new_score
                    best_col = col

            return value, best_col

        else:  # Minimizing
            value = math.inf
            best_col = valid_locations[len(valid_locations) // 2]

            for col in self._order_moves(valid_locations):
                self.nodes_expanded += 1
                temp2 = GameEngine()
                temp2.board = board.copy()
                temp2.drop_piece(col, PLAYER)
                new_score, _ = self._minimax(temp2.board, depth - 1, True)
                if new_score < value:
                    value = new_score
                    best_col = col

            return value, best_col

    #Minimax with Alpha-Beta Pruning

    def _minimax_ab(self, board, depth: int, alpha: float, beta: float,
                    maximizing: bool) -> tuple[int, int]:
        temp = GameEngine()
        temp.board = board

        valid_locations = temp.get_valid_locations()
        gameover = temp.is_terminal_node()

        #Base Cases
        if is_terminal:
            self.nodes_expanded += 1
            if temp.check_win(AI):
                return (10_000_000 + depth, None)
            elif temp.check_win(PLAYER):
                return (-10_000_000 - depth, None)
            else:
                return (0, None)

        if depth == 0:
            self.nodes_expanded += 1
            return (score_board(board, AI, self.weights), None)

        # Recursive Cases with Pruning 
        if maximizing:
            best_score = -99999999
            best_col = valid_locations[len(valid_locations) // 2]

            for col in self._order_moves(valid_locations):
                self.nodes_expanded += 1
                temp2 = GameEngine()
                temp2.board = board.copy()
                temp2.drop_piece(col, AI)
                new_score, _ = self._minimax_ab(temp2.board, depth - 1, alpha, beta, False)

                if new_score > value:
                    value = new_score
                    best_col = col

                alpha = max(alpha, value)

                #PRUNING
                if alpha >= beta:
                    break

            return value, best_col

        else:  # Minimizing
            value = math.inf
            best_col = valid_locations[len(valid_locations) // 2]

            for col in self._order_moves(valid_locations):
                self.nodes_expanded += 1
                temp2 = GameEngine()
                temp2.board = board.copy()
                temp2.drop_piece(col, PLAYER)
                new_score, _ = self._minimax_ab(temp2.board, depth - 1, alpha, beta, True)

                if new_score < value:
                    value = new_score
                    best_col = col

                beta = min(beta, value)

                #PRUNING
                if alpha >= beta:
                    break

            return value, best_col
# Move Ordering: This is an optimization for Alpha-Beta.
# By checking the center columns first, we find the 'best' moves earlier,
# which allows the algorithm to prune (skip) more branches.
    def _order_moves(self, valid_locations: list) -> list:
        
        center = COLS // 2
        return sorted(valid_locations, key=lambda col: abs(col - center))
