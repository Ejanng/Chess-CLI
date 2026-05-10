# ♟️ Automaton Chess Engine (CLI)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen)]()

> A fully functional command-line chess game built in Python, implementing core chess mechanics through the lens of **Automata Theory** — DFA, NFA, PDA, and formal state encoding.

---

## 🎯 Project Overview

This project was developed as a **1-week academic/technical challenge** to bridge theoretical computer science (automata theory) with practical software engineering. Every major component maps directly to an automaton concept:

| Chess Concept | Automaton Equivalent | Implementation |
|-------------|---------------------|----------------|
| **Board Position** | DFA State | `board.py` — 8×8 grid state representation |
| **Legal Move Check** | DFA Transition δ | `main/DFA_move_validator.py` — deterministic validation pipeline |
| **Game Tree Search** | NFA State Exploration | `ai_engine.py` — minimax with α-β pruning |
| **Move History / Undo** | PDA Stack Operations | `game_engine.py` — push/pop state snapshots |
| **Save/Load Games** | FEN State Encoding | `state_manager.py` — Forsyth-Edwards Notation |

---

## ✨ Features

### Gameplay
- ✅ **Human vs AI** — Play against a computer opponent with adjustable difficulty (depth 1–5)
- ✅ **Human vs Human** — Two-player mode on the same machine
- ✅ **Full Legal Move Validation** — All standard chess rules including special moves
- ✅ **Special Moves** — Castling, en passant, pawn promotion (CLI prompts for choice; AI auto-queen)
- ✅ **Check / Checkmate / Stalemate Detection** — Automatic game-end detection
- ✅ **Undo Move** — Revert to previous positions (PDA stack pop)

### AI Engine
- ✅ **Minimax Algorithm** — Adversarial search for optimal play
- ✅ **Alpha-Beta Pruning** — Efficient branch elimination (NFA pruning)
- ✅ **Adjustable Depth** — Choose search depth (1 = easy, 5 = challenging)
- ✅ **Position Evaluation** — Material + positional scoring

### Standalone DFA Validator
- ✅ **CLI with Visual Traces** — Boxed ASCII DFA execution trace for every move attempt
- ✅ **Optional Tkinter GUI** — Interactive board, DFA state diagram, and move history
- ✅ **FEN File Loading** — Load any position for targeted validation
- ✅ **SVG Diagram Generation** — Visual diagram of the 5-state DFA pipeline

### Persistence
- ✅ **FEN Save/Load** — Export and import games using standard FEN notation
- ✅ **Move History** — Track all moves in algebraic notation

---

## 🗂️ Project Structure

```
chess_automaton/
├── main.py                       # CLI entry point & game loop
├── board.py                      # Board state representation (DFA State)
├── pieces.py                     # Piece classes with move generators (DFA Transitions)
├── validator.py                  # Thin re-export: from main.DFA_move_validator import MoveValidator
├── game_engine.py                # State machine — turn management, special moves, undo
├── ai_engine.py                  # NFA exploration — minimax with α-β pruning
├── state_manager.py              # FEN save/load persistence
├── utils.py                      # Notation parser, display helpers, coordinate conversion
├── README.md                     # This file
├── WRITE_UP.md                   # Deep-dive technical reference for the DFA validator
├── AGENTS.md                     # Coding agent guidance
└── main/                         # Subpackage: enhanced DFA validator + GUI + diagram generator
    ├── __init__.py               # Package init
    ├── DFA_move_validator.py     # ~1,484-line standalone validator (CLI + Tkinter GUI)
    ├── generate_dfa_diagram.py   # SVG diagram generator for the DFA pipeline
    ├── DFA_diagram.svg           # Generated visual diagram of the DFA states
    └── sample_position.fen       # Example FEN file
```

### File Responsibilities

| File | Lines | Purpose | Automaton Role |
|------|-------|---------|---------------|
| `utils.py` | ~69 | Notation parser, ASCII renderer, coord conversion | Helpers |
| `pieces.py` | ~218 | 6 piece classes with rule-based move generation | **DFA δ transitions** |
| `board.py` | ~121 | 8×8 grid, FEN parser, state copying | **DFA State** |
| `validator.py` | ~1 | Re-export of `MoveValidator` from `main.DFA_move_validator` | **DFA Validator proxy** |
| `game_engine.py` | ~267 | Turn management, special moves, undo/redo | **State Machine + PDA** |
| `ai_engine.py` | ~205 | Minimax search, α-β pruning, evaluation | **NFA Explorer** |
| `state_manager.py` | ~123 | FEN encode/decode, file I/O | **State Encoder** |
| `main.py` | ~219 | CLI interface, menu system, command handler | **Interface** |
| `main/DFA_move_validator.py` | ~1,484 | Self-contained DFA validator, CLI/GUI | **DFA Validator (canonical)** |
| `main/generate_dfa_diagram.py` | ~260 | SVG generator for the DFA pipeline | **Diagram** |

**Total: ~2,969 lines of Python**

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

### Running the Full Chess Game (CLI)

```bash
python main.py
```

### Running the Standalone DFA Validator (CLI)

```bash
# Default sample position
python main/DFA_move_validator.py

# Custom FEN file
python main/DFA_move_validator.py my_position.fen

# As a module
python -m main.DFA_move_validator my_position.fen
```

### Running the Standalone DFA Validator (GUI)

```bash
python main/DFA_move_validator.py --gui
python -m main.DFA_move_validator --gui my_position.fen
```

### Regenerating the DFA Diagram SVG

```bash
python main/generate_dfa_diagram.py
```
- Writes `main/DFA_diagram.svg`.

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

| Command | Alias | Action |
|---------|-------|--------|
| `e2e4` | — | Make a move (from square to square) |
| `e2-e4` | — | Alternative move format |
| `save` | `s` | Save current game to FEN file |
| `load` | `l` | Load game from FEN file |
| `undo` | `u` | Undo last move (and AI move if in AI mode) |
| `fen` | `f` | Display current FEN string |
| `board` | `b` | Redisplay the chess board |
| `help` | `h` | Show help menu |
| `quit` | `q` | Exit the game |

---

## 📖 Function Reference

### `main.py` — CLI Entry Point

`main.py` is the full chess game's command-line interface. It wires together the game engine, AI engine, and state manager into an interactive loop.

| Function | Description |
|----------|-------------|
| `print_banner()` | Prints the ASCII title banner at startup. |
| `print_help()` | Displays the command reference and special-move instructions. |
| `get_promotion_choice()` | Prompts the user to choose a promotion piece (`q`/`r`/`b`/`n`). Defaults to Queen. |
| `main()` | **Main game loop.** Sets up the engine, selects game mode, configures AI depth, then loops: AI turn (if active) → human input → command dispatch → move validation → board display → game-over detection. Handles `quit`, `help`, `board`, `fen`, `undo`, `save`, `load`, and move parsing. |

**Key behavior in `main()`:**
- On `undo` in AI mode, undoes twice to revert both the AI's move and the player's move.
- On `load`, resets the move log and recreates the validator so the loaded board is fully synchronized.
- Detects pawn promotion by checking if a Pawn reaches the final rank before calling `engine.make_move()`.

---

### `main/DFA_move_validator.py` — Standalone DFA Validator

This ~1,484-line module is intentionally **self-contained**. It re-implements board logic, piece classes, and the full DFA validation pipeline so it can run standalone for educational demonstration.

#### Helper Functions

| Function | Description |
|----------|-------------|
| `square_to_coords(square)` | Converts algebraic notation (`e4`) to zero-based `(row, col)`. Returns `None` on invalid input. |
| `coords_to_square(row, col)` | Converts `(row, col)` back to algebraic notation. Returns `None` if out of bounds. |
| `parse_move_input(move_str)` | Parses `e2e4` or `e2-e4` into `((from_r, from_c), (to_r, to_c))`. Uses regex `([a-h][1-8])-?([a-h][1-8])`. |
| `piece_title(piece)` | Returns a human-readable label like `"White Pawn"`. |
| `piece_symbol(piece_type, color)` | Returns the correct Unicode chess symbol (e.g., `♔`, `♚`). |

#### Piece Classes

All inherit from `Piece(color, piece_type)` and implement `get_possible_moves(row, col, board)`.

| Class | Key Logic |
|-------|-----------|
| `Pawn` | Forward 1, forward 2 from start rank, diagonal capture, en passant detection via `board.en_passant_target`. |
| `Knight` | 8 L-shaped offsets; can jump over pieces. |
| `Bishop` | Diagonal `_slide()` along 4 directional vectors. |
| `Rook` | Orthogonal `_slide()` along 4 directional vectors. |
| `Queen` | Reuses `Bishop._slide()` + `Rook._slide()` combined. |
| `King` | 1 square any direction; castling (2-square horizontal) when rights, rook, and path are valid. |

#### `Board` Class

| Method | Description |
|--------|-------------|
| `from_fen(fen_string)` | Class method. Parses a FEN string into a fully populated `Board` instance including piece placement, active color, castling rights, en passant target, halfmove clock, and fullmove number. |
| `load_from_file(filename)` | Class method. Reads the first line of a file as FEN and calls `from_fen()`. |
| `copy()` | Deep-copies the board, preserving grid state, piece `has_moved` flags, castling rights, en passant target, and clock counters. |
| `get_piece(row, col)` | Returns the piece at `(row, col)` or `"."` if empty. |
| `set_piece(row, col, piece)` | Places a piece on the grid. |
| `find_king(color)` | Scans the grid to locate the king of the given color. |
| `display()` | Returns a Unicode ASCII art board with rank/file labels. |
| `apply_move(from_coords, to_coords)` | Executes a move, updates `has_moved`, handles castling rook movement, en passant capture, pawn promotion (auto-Queen), and revokes castling rights when king or rooks move. |

#### `MoveValidator` Class — The DFA Engine

| Method | Description |
|--------|-------------|
| `validate(move_str)` | **Full 5-state DFA pipeline.** Returns `(is_valid, trace, error_msg)`. Stages: S0 INPUT (parse) → S1 BOUNDS → S2 PIECE (color check) → S3 RULES (piece geometry) → S4 SAFETY (king check simulation). On first failure, halts and marks remaining states as "(skipped)". |
| `is_valid_move(from_coords, to_coords)` | Programmatic shortcut; no string parsing, no trace. Returns boolean. |
| `simulate_move(from_sq, to_sq)` | Returns a copied `Board` with the move applied (used for king-safety simulation). |
| `is_king_in_check(board, color)` | Checks whether the king of `color` is under attack on the given board. |
| `is_in_check(color)` | Convenience wrapper using the validator's current board. |
| `has_any_legal_moves(color)` | Returns `True` if `color` has at least one legal move in the current position. |
| `get_all_legal_moves(color)` | Generates every `((from_r, from_c), (to_r, to_c))` that passes all 5 DFA stages. |
| `_validate_rules(from_coords, to_coords, piece)` | Delegates to piece-specific validators (`_validate_pawn_move`, `_validate_slider_move`, `_validate_king_move`). |
| `_would_leave_king_in_check(from_coords, to_coords, piece)` | Simulates the move on a copied board and returns `True` if the moving side's king would be in check. |
| `_is_square_attacked(board, row, col, defending_color)` | Checks if any opponent piece attacks `(row, col)`. |

#### Trace Rendering Functions

| Function | Description |
|----------|-------------|
| `render_trace(trace, accepted, ...)` | Builds the boxed ASCII trace output with Unicode box-drawing characters. |
| `normalize_trace(trace)` | Ensures all 5 DFA states appear in the trace map; missing states become `(—, "Awaiting traversal")`. |
| `summary_text(accepted, ...)` | One-line result summary for CLI and GUI surfaces. |
| `print_turn_prompt(board)` | Prints `\n{Color} to move.` |
| `load_board_or_exit(fen_path)` | Loads a board from a FEN file; returns `None` on failure. |

#### CLI & GUI Entry Points

| Function / Class | Description |
|------------------|-------------|
| `run_cli(fen_path)` | Loads a position, prints the board, and loops reading moves. On each input, runs `MoveValidator.validate()`, prints the boxed trace, and (if legal) applies the move to the board. Accepts `quit` to exit. |
| `DfaTraversalApp` | **Tkinter GUI class.** Builds a multi-panel interface: board grid, move input, DFA stepper canvas, state details list, rendered trace box, and move history. Colors nodes green (✓), red (✗), or gray (—) and refreshes dynamically after each validation. |
| `run_gui(fen_path)` | Lazily imports `tkinter`, creates the root window, instantiates `DfaTraversalApp`, and starts `mainloop()`. |
| `parse_args(argv)` | Parses `--gui` flag and optional FEN file path from command-line arguments. |
| `main(argv)` | Dispatches to `run_gui()` or `run_cli()` based on parsed arguments. |

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

### DFA State Diagram

![DFA Pipeline Diagram](main/DFA_diagram.svg)

> The SVG above visualizes the 5-state validation pipeline: **S0 INPUT → S1 BOUNDS → S2 PIECE → S3 RULES → S4 SAFETY**. Green edges represent accept transitions; red edges represent reject transitions. Regenerate it anytime with `python main/generate_dfa_diagram.py`.

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
│  (main/DFA_move_      │  (ai_engine.py)                       │
│   validator.py)       │  Minimax → α-β Pruning → Eval         │
│  Bounds → Rules →     │  Game Tree Exploration                │
│  King Safety Check    │                                       │
├───────────────────────┴───────────────────────────────────────┤
│  LAYER 4: Board & Pieces (board.py, pieces.py)              │
│  8×8 Grid • Piece Classes • Move Generators • FEN Codec     │
├─────────────────────────────────────────────────────────────┤
│  LAYER 5: Utilities (utils.py, state_manager.py)            │
│  Notation Parser • Display Helpers • FEN Save/Load          │
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

## 📚 Documentation

| File | Audience | Contents |
|------|----------|----------|
| `README.md` | Human users | Project overview, features, getting started, architecture diagram |
| `WRITE_UP.md` | Developers | Deep-dive technical reference for `main/DFA_move_validator.py`, including the 5-state DFA pipeline, error codes, class reference, and usage examples |
| `AGENTS.md` | AI coding agents | Architecture, conventions, and practical guidance for making changes |

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

This project is licensed under the MIT License.

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
