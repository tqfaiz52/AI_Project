# Connect 4 — Game Playing AI using Adversarial Search
## Academic Project | Artificial Intelligence Course

---

## Project Structure

```
connect4/
├── game_engine.py          # Student 1: Board logic, rules, win detection
├── ai_agent.py             # Student 2: Minimax + Alpha-Beta Pruning (from scratch)
├── heuristic.py            # Student 3: Evaluation functions + weight presets
├── main.py                 # Student 4: Pygame GUI + research panel
├── research_benchmark.py   # Student 4: Standalone research data generator
└── README.md
```

---

## Setup

```bash
pip install pygame numpy
python main.py
```

To generate research data (for report):
```bash
python research_benchmark.py
```

---

## How to Play

- **Click any column** in the board to drop your piece (Red)
- The AI (Blue) responds instantly using Minimax/Alpha-Beta
- Press **N** to start a new game

---

## Research Panel (Right Side)

The GUI includes a live research panel showing:

| Metric | Description |
|--------|-------------|
| Nodes Expanded | How many board states the AI evaluated |
| Nodes Saved | How many branches Alpha-Beta pruned away |
| Node History | Bar chart comparing both algorithms per move |
| Heuristic Weights | Visual display of current scoring parameters |

---

## AI Settings

### Search Depth
- **Depth 3**: Fast, beginner-level (~0.1s per move)
- **Depth 5**: Strong, responds in ~0.5s *(default)*
- **Depth 7**: Very strong, may take 2-3s per move

### Algorithm
- **Alpha-Beta ON**: Finds the same move as Minimax but explores far fewer nodes
- **Pure Minimax**: No pruning — explores the entire game tree (much slower)

### Heuristic Presets (tested for win rate comparison)
| Preset | Description |
|--------|-------------|
| Balanced | Equal weight on offense and defense |
| Aggressive | Prioritizes building own threats |
| Defensive | Prioritizes blocking opponent threats |
| Center-Heavy | Strong center column preference |

---

## Algorithm Details

### Minimax
Explores ALL possible moves up to depth `d`. At each level, the AI
picks the move that maximizes its score; the human picks the move that
minimizes it. Complexity: **O(b^d)** where b≈7 (branching factor).

### Alpha-Beta Pruning
Augments Minimax with two bounds:
- **α (alpha)**: Best score the AI can guarantee
- **β (beta)**: Best score the human can guarantee

If `β ≤ α`, the current branch is **pruned** — a rational opponent
would never allow it, so there is no point evaluating it further.

**Mathematical guarantee**: Finds the SAME best move as pure Minimax.
**Complexity**: **O(b^(d/2))** with perfect move ordering.

### Heuristic Evaluation Function
When the search hits its depth limit, the board is scored by:
1. **Center control** — center column pieces get a bonus
2. **Window analysis** — every possible 4-cell window is scored:
   - 4 pieces = win (1,000,000 pts)
   - 3 + 1 empty = strong threat (+50 pts)
   - 2 + 2 empty = potential (+10 pts)
   - Opponent 3 + 1 empty = block urgently (−80 pts)

---

## Research Findings (from benchmark script)

| Depth | Minimax Nodes | Alpha-Beta Nodes | Reduction |
|-------|--------------|-----------------|-----------|
| 3     | ~800         | ~200            | ~75%      |
| 5     | ~50,000      | ~3,000          | ~94%      |
| 7     | ~2,000,000   | ~50,000         | ~97.5%    |

**Horizon Effect**: At depth 3, the AI sometimes makes strategically
poor moves because a fatal trap is only visible at depth 4 or 5.
This is a known limitation of fixed-depth adversarial search.

---

## Dependencies

- `pygame` — GUI and event handling
- `numpy` — Board representation (2D array)
- No ML libraries used — algorithms are pure recursive logic
