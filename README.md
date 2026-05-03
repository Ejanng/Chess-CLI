# ♟️ Automaton Chess Engine (CLI)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen)]()

> A fully functional command-line chess game built in Python, implementing core chess mechanics through the lens of **Automata Theory** — DFA, NFA, PDA, and formal state encoding.

---

## 🎯 Project Overview

This project was developed as a **1-week academic/technical challenge** to bridge theoretical computer science (automata theory) with practical software engineering. Every major component maps directly to an automaton concept:

| Chess Concept | Automaton Equivalent | Implementation |
|-------------|---------------------|----------------|
| **Board Position** | DFA State | `board.py` — 8×8 grid state representation |
| **Legal Move Check** | DFA Transition δ | `validator.py` — deterministic validation pipeline |
| **Game Tree Search** | NFA State Exploration | `ai_engine.py` — minimax with α-β pruning |
| **Move History / Undo** | PDA Stack Operations | `game_engine.py` — push/pop state snapshots |
| **Save/Load Games** | FEN State Encoding | `state_manager.py` — Forsyth-Edwards Notation |

---

## ✨ Features

### Gameplay
- ✅ **Human vs AI** — Play against a computer opponent with adjustable difficulty (depth 1–5)
- ✅ **Human vs Human** — Two-player mode on the same machine
- ✅ **Full Legal Move Validation** — All standard chess rules including special moves
- ✅ **Special Moves** — Castling, en passant, pawn promotion (auto-queen)
- ✅ **Check / Checkmate / Stalemate Detection** — Automatic game-end detection
- ✅ **Undo Move** — Revert to previous positions (PDA stack pop)

### AI Engine
- ✅ **Minimax Algorithm** — Adversarial search for optimal play
- ✅ **Alpha-Beta Pruning** — Efficient branch elimination (NFA pruning)
- ✅ **Adjustable Depth** — Choose search depth (1 = easy, 5 = challenging)
- ✅ **Position Evaluation** — Material + positional scoring

### Persistence
- ✅ **FEN Save/Load** — Export and import games using standard FEN notation
- ✅ **Move History** — Track all moves in algebraic notation

---

## 🗂️ Project Structure

```
chess_automaton/
├── main.py              # CLI entry point & game loop
├── board.py             # Board state representation (DFA State)
├── pieces.py            # Piece classes with move generators (DFA Transitions)
├── validator.py         # DFA move validation engine
├── game_engine.py       # State machine — turn management, special moves, undo
├── ai_engine.py         # NFA exploration — minimax with α-β pruning
├── state_manager.py     # FEN save/load persistence
└── utils.py             # Notation parser, display helpers, coordinate conversion
```

### File Responsibilities

| File | Lines | Purpose | Automaton Role |
|------|-------|---------|---------------|
| `utils.py` | ~75 | Notation parser, ASCII renderer, coord conversion | Helpers |
| `pieces.py` | ~180 | 6 piece classes with rule-based move generation | **DFA δ transitions** |
| `board.py` | ~120 | 8×8 grid, FEN parser, state copying | **DFA State** |
| `validator.py` | ~200 | Bounds, piece rules, king safety checks | **DFA Validator** |
| `game_engine.py` | ~250 | Turn management, special moves, undo/redo | **State Machine + PDA** |
| `ai_engine.py` | ~220 | Minimax search, α-β pruning, evaluation | **NFA Explorer** |
| `state_manager.py` | ~130 | FEN encode/decode, file I/O | **State Encoder** |
| `main.py` | ~200 | CLI interface, menu system, command handler | **Interface** |

**Total: ~1,375 lines of Python**

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Terminal with Unicode support (for chess symbols)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/automaton-chess-engine.git
cd automaton-chess-engine

# No external dependencies required — uses only Python standard library!
```

### Running the Game

```bash
python main.py
```

### Sample Session

```
    ╔═══════════════════════════════════════════════════════════╗
    ║           AUTOMATON CHESS ENGINE v1.0                     ║
    ║     Deterministic & Non-deterministic Finite Automata     ║
    ║                    CLI Edition                            ║
    ╚═══════════════════════════════════════════════════════════╝

Select game mode:
  1. Human (White) vs AI (Black)
  2. Human vs Human
Enter choice [1]: 1
AI difficulty (1-5, default 3): 3
AI opponent ready (depth=3)

==================================================
  a b c d e f g h
  ---------------
8|r n b q k b n r|8
7|p p p p p p p p|7
6|. . . . . . . .|6
5|. . . . . . . .|5
4|. . . . . . . .|4
3|. . . . . . . .|3
2|P P P P P P P P|2
1|R N B Q K B N R|1
  ---------------
  a b c d e f g h

White to move.

White> e2e4
Move: e2e4

[AI thinking...]
AI plays: e7e5
Nodes evaluated: 1247
```

---

## 🎮 Controls & Commands

| Command | Action |
|---------|--------|
| `e2e4` | Make a move (from square to square) |
| `e2-e4` | Alternative move format |
| `save` | Save current game to FEN file |
| `load` | Load game from FEN file |
| `undo` | Undo last move (and AI move if in AI mode) |
| `fen` | Display current FEN string |
| `board` | Redisplay the chess board |
| `help` | Show help menu |
| `quit` | Exit the game |

---

## 🧠 Automaton Theory Deep Dive

### 1. Deterministic Finite Automaton (DFA) — Move Validation

The move validator implements a **5-state DFA**:

```
Input → Bounds Check → Piece Check → Move Rules DFA → King Safety Check → {Accept, Reject}
```

- **States**: Validation stages (parsed, bounded, owned, ruled, safe)
- **Alphabet**: Chess moves in algebraic notation (e.g., `e2e4`)
- **Transition Function δ**: Each validation stage is a deterministic step
- **Accept State**: Move is legal AND king is safe after execution
- **Reject State**: Any validation fails

**Key insight**: The `Piece.get_possible_moves()` method is itself a DFA transition function — given a piece type, position, and board state, it deterministically outputs all valid destination squares.

### 2. Non-deterministic Finite Automaton (NFA) — AI Search

The game tree is an **NFA** where each node non-deterministically branches into all legal moves:

```
S₀ --[e2e4]--> S₁₁ --[e7e5]--> S₂₁₁ --[Nf3]--> S₃₁₁₁ (+0.5 eval)
   |            |             |
   |            |             +--[Bc4]--> S₃₁₁₂ (+0.2 eval)  ✗ [pruned]
   |            |
   |            +--[d7d5]--> S₂₁₂ --[exd5]--> ...
   |
   +--[d2d4]--> S₁₂ --[d7d5]--> ...
```

- **Minimax**: Resolves NFA non-determinism by choosing optimal paths
- **α-β Pruning**: Eliminates NFA branches that cannot improve the outcome
- **Position Evaluation**: Weighted automaton output scoring material + position

### 3. Pushdown Automaton (PDA) — Move History

Move history uses a **stack** (LIFO) for undo functionality:

```
PDA = (Q, Σ, Γ, δ, q₀, Z₀, F)
- Q = {game states}
- Σ = {chess moves}
- Γ = {state snapshots}
- δ: (state, move, stack_top) → (new_state, push/pop)
- Z₀ = empty stack
```

**Operations**:
- **PUSH**: On every move, save board snapshot + metadata to `move_history[]`
- **POP**: On undo, pop last snapshot and restore board state

### 4. FEN — Compact State Encoding

[Forsyth-Edwards Notation](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation) encodes a complete DFA state in ~80 characters:

```
rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e3 0 1
│           │           │    │    │    │    │
│           │           │    │    │    │    └── Fullmove number
│           │           │    │    │    └────── Halfmove clock (50-move rule)
│           │           │    │    └─────────── En passant target square
│           │           │    └──────────────── Castling rights (KQkq)
│           │           └────────────────────── Active color (w/b)
│           └────────────────────────────────── Piece placement (8 rows)
└──────────────────────────────────────────── Row 8: rnbqkbnr
```

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: CLI Interface (main.py)                           │
│  Input Parser • Display Renderer • Command Handler          │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: Game Engine (game_engine.py)                      │
│  Turn Management • State Transitions • Special Moves        │
│  Game End Detection • Move History (Undo)                   │
├───────────────────────┬───────────────────────────────────────┤
│  LAYER 3: DFA         │  LAYER 3: NFA                         │
│  Move Validator       │  AI Engine                            │
│  (validator.py)       │  (ai_engine.py)                       │
│  Bounds → Rules →     │  Minimax → α-β Pruning → Eval         │
│  King Safety Check    │  Game Tree Exploration                │
├───────────────────────┴───────────────────────────────────────┤
│  LAYER 4: Board & Pieces (board.py, pieces.py)              │
│  8×8 Grid • Piece Classes • Move Generators • FEN Codec     │
├─────────────────────────────────────────────────────────────┤
│  LAYER 5: Utilities (utils.py, state_manager.py)            │
│  Notation Parser • Display Helpers • FEN Save/Load        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing & Validation

The engine has been tested against:
- ✅ Standard starting position (all 20 legal opening moves)
- ✅ Castling (kingside & queenside, with rights validation)
- ✅ En passant capture
- ✅ Pawn promotion
- ✅ Check detection (discovered checks, double check)
- ✅ Checkmate and stalemate recognition
- ✅ 50-move rule implementation
- ✅ FEN round-trip consistency (save → load produces identical state)

---

## 📚 Educational Value

This project demonstrates:

| Theory | Practical Application |
|--------|----------------------|
| **DFA Design** | Move validation pipeline with accept/reject states |
| **NFA to DFA** | Game tree exploration with deterministic minimax resolution |
| **PDA Stack** | LIFO move history for undo operations |
| **State Encoding** | FEN as a bijective state-space compression |
| **Complexity Analysis** | O(b^d) minimax vs O(b^(d/2)) α-β pruning |

---

## 🔮 Future Enhancements

- [ ] Opening book integration (precomputed DFA transitions)
- [ ] Endgame tablebases (perfect play for ≤7 pieces)
- [ ] Iterative Deepening Search (IDS)
- [ ] Transposition tables (FEN-based hashing)
- [ ] UCI protocol support (play against other engines)
- [ ] GUI using `curses` or `pygame`
- [ ] Neural network evaluation (replace weighted automaton)

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Built as a 1-week sprint project for automata theory coursework
- Inspired by classical chess engine architecture (Stockfish, Crafty)
- FEN specification based on [Forsyth-Edwards Notation standard](https://www.chessprogramming.org/Forsyth-Edwards_Notation)

---

<div align="center">

**Made with ♟️ and automata theory**

[⬆ Back to Top](#-automaton-chess-engine-cli)

</div>
