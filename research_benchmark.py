
import time
import random
from game_engine import GameEngine, AI, PLAYER
from ai_agent import AIAgent
from heuristic import HEURISTIC_PRESETS


def separator(title=""):
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)


def run_node_comparison(depth: int = 5, num_positions: int = 10):
   
    separator(f"NODE EXPANSION COMPARISON  (depth={depth})")
    print(f"  Testing {num_positions} random mid-game positions\n")
    print(f"  {'Pos':>4}  {'Minimax':>12}  {'Alpha-Beta':>12}  {'Reduction':>10}  {'Speedup':>8}")
    print("  " + "-" * 52)

    ab_totals   = []
    pure_totals = []

    for pos in range(num_positions):
        engine = GameEngine()

        # Make 8-12 random moves to get a mid-game position
        n_moves = random.randint(8, 14)
        for _ in range(n_moves):
            valid = engine.get_valid_locations()
            if not valid or engine.is_terminal_node():
                break
            col = random.choice(valid)
            piece = PLAYER if engine.turn == PLAYER else AI
            engine.drop_piece(col, piece)
            engine.turn = AI if engine.turn == PLAYER else PLAYER

        if engine.is_terminal_node():
            continue

        # Run both algorithms
        ai_ab   = AIAgent(depth=depth, use_alpha_beta=True)
        ai_pure = AIAgent(depth=depth, use_alpha_beta=False)

        ai_ab.get_move(engine)
        ai_pure.get_move(engine)

        ab_n   = ai_ab.nodes_expanded
        pure_n = ai_pure.nodes_expanded

        ab_totals.append(ab_n)
        pure_totals.append(pure_n)

        reduction = 100 * (pure_n - ab_n) / pure_n if pure_n > 0 else 0
        speedup   = pure_n / ab_n if ab_n > 0 else 1

        print(f"  {pos+1:>4}  {pure_n:>12,}  {ab_n:>12,}  {reduction:>9.1f}%  {speedup:>7.1f}x")

    if ab_totals:
        avg_ab   = sum(ab_totals)   / len(ab_totals)
        avg_pure = sum(pure_totals) / len(pure_totals)
        averagereductionpct  = 100 * (avg_pure - avg_ab) / avg_pure
        averagespeedup  = avg_pure / avg_ab

        print("  " + "-" * 52)
        print(f"  {'AVG':>4}  {avg_pure:>12,.0f}  {avg_ab:>12,.0f}  {averagereductionpct:>9.1f}%  {averagespeedup:>7.1f}x")
        print(f"\n Alpha-Beta pruned {averagereductionpct:.1f}% of nodes on average")
        print(f" Alpha-Beta is ~{averagespeedup:.1f}x faster than pure Minimax")


def run_depth_scaling():
    
    #Show how node counts scale with depth for both algorithms.
    #Demonstrates the O(b^d) vs O(b^(d/2)) complexity difference.
    
    separator("DEPTH SCALING ANALYSIS")
    print(f"  {'Depth':>6}  {'Minimax':>14}  {'Alpha-Beta':>14}  {'Ratio':>8}")
    print("  " + "-" * 48)

    engine = GameEngine()
    # Drop a few pieces to make it non-trivial
    for col in [3, 3, 2, 4, 1, 5]:
        piece = PLAYER if engine.turn == PLAYER else AI
        engine.drop_piece(col, piece)
        engine.turn = AI if engine.turn == PLAYER else PLAYER

    for depth in range(1, 8):
        ai_ab   = AIAgent(depth=depth, use_alpha_beta=True)
        ai_pure = AIAgent(depth=depth, use_alpha_beta=False)

        ai_ab.get_move(engine)
        ai_pure.get_move(engine)

        ratio = ai_pure.nodes_expanded / max(ai_ab.nodes_expanded, 1)
        print(f"  {depth:>6}  {ai_pure.nodes_expanded:>14,}  {ai_ab.nodes_expanded:>14,}  {ratio:>7.1f}x")


def run_heuristic_tournament(games_per_matchup: int = 20):
    
    separator("HEURISTIC PRESET COMPARISON")
    print(f"  Each preset plays {games_per_matchup} games vs random opponent\n")
    print(f"  {'Heuristic':<20}  {'Wins':>6}  {'Draws':>6}  {'Losses':>7}  {'Win%':>6}")
    print("  " + "-" * 56)

    for name, weights in HEURISTIC_PRESETS.items():
        wins = draws = losses = 0

        for game_num in range(games_per_matchup):
            engine = GameEngine()
            ai = AIAgent(depth=4, use_alpha_beta=True, weights=weights)

            while not engine.game_over:
                if engine.turn == PLAYER:
                    # Random opponent
                    valid = engine.get_valid_locations()
                    if not valid:
                        break
                    col = random.choice(valid)
                    engine.drop_piece(col, PLAYER)
                    if engine.check_win(PLAYER):
                        losses += 1
                        engine.game_over = True
                    elif engine.is_draw():
                        draws += 1
                        engine.game_over = True
                    else:
                        engine.turn = AI
                else:
                    col, _ = ai.get_move(engine)
                    engine.drop_piece(col, AI)
                    if engine.check_win(AI):
                        wins += 1
                        engine.game_over = True
                    elif engine.is_draw():
                        draws += 1
                        engine.game_over = True
                    else:
                        engine.turn = PLAYER

        win_pct = 100 * wins / games_per_matchup
        short = name.split("(")[0].strip()
        print(f"  {short:<20}  {wins:>6}  {draws:>6}  {losses:>7}  {win_pct:>5.0f}%")


def run_timing_benchmark():
    
    separator("TIMING BENCHMARK")
    print(f"  {'Depth':>6}  {'Minimax (ms)':>14}  {'AlphaBeta (ms)':>16}  {'Speedup':>8}")
    print("  " + "-" * 50)

    engine = GameEngine()
    for col in [3, 2, 3, 4]:
        piece = PLAYER if engine.turn == PLAYER else AI
        engine.drop_piece(col, piece)
        engine.turn = AI if engine.turn == PLAYER else PLAYER

    for depth in [3, 4, 5, 6, 7]:
        ai_ab   = AIAgent(depth=depth, use_alpha_beta=True)
        ai_pure = AIAgent(depth=depth, use_alpha_beta=False)

        t0 = time.perf_counter()
        ai_pure.get_move(engine)
        t_pure = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        ai_ab.get_move(engine)
        t_ab = (time.perf_counter() - t0) * 1000

        speedup = t_pure / max(t_ab, 0.001)
        print(f"  {depth:>6}  {t_pure:>14.1f}  {t_ab:>16.1f}  {speedup:>7.1f}x")


if __name__ == "__main__":
    print("\n" + " " * 60)
    print("  CONNECT 4 AI ADVERSARIAL SEARCH RESEARCH REPORT")
    print("  Minimax vs Alpha-Beta Pruning Analysis")
 

    random.seed(31686)  # Reproducible results

    run_node_comparison(depth=5, num_positions=8)
    run_depth_scaling()
    run_timing_benchmark()
    run_heuristic_tournament(games_per_matchup=30)

