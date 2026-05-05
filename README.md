
# Connect 4 — Game Playing AI using Adversarial Search
## Project Structure

```
connect4/
├── game_engine.py         
├── ai_agent.py             
├── heuristic.py            
├── main.py                 
├── research_benchmark.py   
└── README.md
```

---

## Setup

```bash
pip install pygame numpy
python main.py
```

To generate research data
```bash
python research_benchmark.py
```

---

## How to Play

- **Click any column** in the board to drop your piece (Red)
- The AI responds instantly using Minimax/Alpha-Beta
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

*Data collected dynamically using `research_benchmark.py` testing multiple mid-game positions.*

| Depth | Minimax Nodes | Alpha-Beta Nodes | Node Reduction | Time Speedup |
|-------|--------------|-----------------|----------------|--------------|
| **3** | 664          | 349             | ~47.4%         | 4.6x faster  |
| **5** | 30,925 (avg) | 2,534 (avg)     | ~91.8%         | 43.2x faster |
| **7** | 1,265,337    | 114,503         | ~90.9%         | 224.6x faster|

**Complexity Proof:** 
At Depth 7, pure Minimax choked, taking over 7.5 minutes to evaluate 1.2+ million nodes. Alpha-Beta Pruning, enhanced by our center-first move ordering, evaluated the exact same optimal move in just ~2 seconds. This practically demonstrates the mathematical optimization from O(b^d) to O(b^(d/2)).

**Heuristic Tournament (Win Rates):** 
We simulated 30 games per heuristic preset against a randomized opponent. Every single preset (Balanced, Aggressive, Defensive, Center-Heavy) achieved a 100% win rate, proving that Depth 4 with Alpha-Beta pruning cannot be beaten by random play.

**Horizon Effect**: At depth 3, the AI sometimes makes strategically
poor moves because a fatal trap is only visible at depth 4 or 5.
This is a known limitation of fixed-depth adversarial search.
---

## Dependencies

- `pygame` — GUI and event handling
- `numpy` — Board representation (2D array)
- No ML libraries used — algorithms are pure recursive logic
