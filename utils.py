"""
utils.py
Chess notation parser and display helpers.
Supports algebraic notation (e.g., 'e2e4') and FEN string handling.
"""

# File: chess_automaton/utils.py

def square_to_coords(square):
    """
    Convert algebraic notation (e.g., 'e4') to board coordinates (row, col).
    Board is 0-indexed: row 0 = rank 8, row 7 = rank 1.
    """
    if len(square) != 2:
        return None
    file = square[0].lower()
    rank = square[1]
    if file < 'a' or file > 'h' or rank < '1' or rank > '8':
        return None
    col = ord(file) - ord('a')      # 0-7
    row = 8 - int(rank)             # 0-7 (rank 8 -> row 0)
    return (row, col)

def coords_to_square(row, col):
    """Convert board coordinates back to algebraic notation."""
    if not (0 <= row <= 7 and 0 <= col <= 7):
        return None
    file = chr(ord('a') + col)
    rank = str(8 - row)
    return file + rank

def parse_move(move_str):
    """
    Parse move string like 'e2e4' or 'e2-e4' into ((from_row, from_col), (to_row, to_col)).
    Returns None if invalid.
    """
    move_str = move_str.replace('-', '').replace(' ', '').lower()
    if len(move_str) != 4:
        return None
    from_sq = move_str[0:2]
    to_sq = move_str[2:4]
    from_coords = square_to_coords(from_sq)
    to_coords = square_to_coords(to_sq)
    if from_coords is None or to_coords is None:
        return None
    return (from_coords, to_coords)

def format_move(from_coords, to_coords):
    """Format coordinates as 'e2e4' string."""
    from_sq = coords_to_square(*from_coords)
    to_sq = coords_to_square(*to_coords)
    if from_sq and to_sq:
        return from_sq + to_sq
    return None

def display_board_ascii(board_grid):
    """
    Return ASCII art representation of the board.
    board_grid is 8x8 list of piece symbols or '.' for empty.
    """
    lines = []
    lines.append("  a b c d e f g h")
    lines.append("  ---------------")
    for i, row in enumerate(board_grid):
        rank = str(8 - i)
        row_str = " ".join(str(cell) if cell != '.' else '.' for cell in row)
        lines.append(f"{rank}| {row_str} |{rank}")
    lines.append("  ---------------")
    lines.append("  a b c d e f g h")
    return "\n".join(lines)

def piece_symbol(piece_type, color):
    """Return Unicode chess symbol for piece."""
    symbols = {
        'white': {'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙'},
        'black': {'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞', 'P': '♟'}
    }
    return symbols.get(color, {}).get(piece_type, '?')