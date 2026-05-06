#!/usr/bin/env python3
"""
@main/DFA_move_validator.py
Deterministic Finite Automaton for Chess Move Validation.
Loads a FEN position, validates user moves through a 5-state DFA pipeline,
and prints a visual execution trace for every attempt.
"""

from __future__ import annotations

import argparse
import re
import sys
import textwrap

tk = None
messagebox = None

DEFAULT_FEN_PATH = "sample_position.fen"
STATE_LABELS = ["S0 INPUT", "S1 BOUNDS", "S2 PIECE", "S3 RULES", "S4 SAFETY"]
PIECE_NAMES = {
    "P": "Pawn",
    "N": "Knight",
    "B": "Bishop",
    "R": "Rook",
    "Q": "Queen",
    "K": "King",
}


def square_to_coords(square):
    """Convert algebraic notation like 'e4' to (row, col)."""
    if len(square) != 2:
        return None
    file_char = square[0].lower()
    rank_char = square[1]
    if file_char < "a" or file_char > "h" or rank_char < "1" or rank_char > "8":
        return None
    return (8 - int(rank_char), ord(file_char) - ord("a"))


def coords_to_square(row, col):
    """Convert (row, col) back to algebraic notation."""
    if not (0 <= row <= 7 and 0 <= col <= 7):
        return None
    return f"{chr(ord('a') + col)}{8 - row}"


def parse_move_input(move_str):
    """Parse 'e2e4' or 'e2-e4' into ((from_r, from_c), (to_r, to_c))."""
    cleaned = move_str.strip().lower()
    match = re.fullmatch(r"([a-h][1-8])-?([a-h][1-8])", cleaned)
    if not match:
        return None
    from_sq, to_sq = match.groups()
    return square_to_coords(from_sq), square_to_coords(to_sq)


def piece_title(piece):
    """Return a human-readable piece label."""
    return f"{piece.color.capitalize()} {PIECE_NAMES[piece.type]}"


def piece_symbol(piece_type, color):
    """Return a Unicode chess symbol for the given piece."""
    symbols = {
        "white": {"K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙"},
        "black": {"K": "♚", "Q": "♛", "R": "♜", "B": "♝", "N": "♞", "P": "♟"},
    }
    return symbols.get(color, {}).get(piece_type, "?")


class Piece:
    """Base class for all chess pieces."""

    def __init__(self, color, piece_type):
        self.color = color
        self.type = piece_type
        self.has_moved = False

    def __repr__(self):
        return f"{self.color[0].upper()}{self.type}"

    def get_possible_moves(self, row, col, board):
        raise NotImplementedError

    def _is_valid_square(self, row, col):
        return 0 <= row <= 7 and 0 <= col <= 7

    def _get_grid(self, board):
        return board.grid if hasattr(board, "grid") else board

    def _get_piece(self, board, row, col):
        if not self._is_valid_square(row, col):
            return None
        return self._get_grid(board)[row][col]

    def _is_empty(self, board, row, col):
        return self._get_piece(board, row, col) == "."

    def _can_capture(self, board, row, col):
        piece = self._get_piece(board, row, col)
        return piece not in (None, ".") and piece.color != self.color


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color, "P")
        self.direction = -1 if color == "white" else 1

    def get_possible_moves(self, row, col, board):
        moves = []
        new_row = row + self.direction

        if self._is_empty(board, new_row, col):
            moves.append((new_row, col))
            start_row = 6 if self.color == "white" else 1
            new_row_2 = row + 2 * self.direction
            if row == start_row and self._is_empty(board, new_row_2, col):
                moves.append((new_row_2, col))

        for delta_col in (-1, 1):
            cap_row = row + self.direction
            cap_col = col + delta_col
            if self._can_capture(board, cap_row, cap_col):
                moves.append((cap_row, cap_col))

        en_passant_target = getattr(board, "en_passant_target", None)
        if en_passant_target:
            ep_row, ep_col = en_passant_target
            if ep_row == row + self.direction and abs(ep_col - col) == 1 and self._is_empty(board, ep_row, ep_col):
                adjacent_piece = self._get_piece(board, row, ep_col)
                if adjacent_piece not in (None, ".") and adjacent_piece.type == "P" and adjacent_piece.color != self.color:
                    moves.append((ep_row, ep_col))

        return moves


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, "N")

    def get_possible_moves(self, row, col, board):
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for delta_row, delta_col in offsets:
            new_row = row + delta_row
            new_col = col + delta_col
            if self._is_valid_square(new_row, new_col):
                if self._is_empty(board, new_row, new_col) or self._can_capture(board, new_row, new_col):
                    moves.append((new_row, new_col))
        return moves


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, "B")

    def get_possible_moves(self, row, col, board):
        return self._slide(row, col, board, [(-1, -1), (-1, 1), (1, -1), (1, 1)])

    def _slide(self, row, col, board, directions):
        moves = []
        for delta_row, delta_col in directions:
            cur_row = row + delta_row
            cur_col = col + delta_col
            while self._is_valid_square(cur_row, cur_col):
                if self._is_empty(board, cur_row, cur_col):
                    moves.append((cur_row, cur_col))
                elif self._can_capture(board, cur_row, cur_col):
                    moves.append((cur_row, cur_col))
                    break
                else:
                    break
                cur_row += delta_row
                cur_col += delta_col
        return moves


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color, "R")

    def get_possible_moves(self, row, col, board):
        return self._slide(row, col, board, [(-1, 0), (1, 0), (0, -1), (0, 1)])

    def _slide(self, row, col, board, directions):
        moves = []
        for delta_row, delta_col in directions:
            cur_row = row + delta_row
            cur_col = col + delta_col
            while self._is_valid_square(cur_row, cur_col):
                if self._is_empty(board, cur_row, cur_col):
                    moves.append((cur_row, cur_col))
                elif self._can_capture(board, cur_row, cur_col):
                    moves.append((cur_row, cur_col))
                    break
                else:
                    break
                cur_row += delta_row
                cur_col += delta_col
        return moves


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color, "Q")

    def get_possible_moves(self, row, col, board):
        return Rook(self.color).get_possible_moves(row, col, board) + Bishop(self.color).get_possible_moves(row, col, board)


class King(Piece):
    def __init__(self, color):
        super().__init__(color, "K")

    def get_possible_moves(self, row, col, board):
        moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for delta_row, delta_col in directions:
            new_row = row + delta_row
            new_col = col + delta_col
            if self._is_valid_square(new_row, new_col):
                if self._is_empty(board, new_row, new_col) or self._can_capture(board, new_row, new_col):
                    moves.append((new_row, new_col))

        castling_rights = getattr(board, "castling_rights", None)
        if castling_rights and not self.has_moved:
            home_row = 7 if self.color == "white" else 0
            if row == home_row and col == 4:
                if castling_rights.get(f"{self.color}_kingside") and self._castle_path_is_clear(board, row, 7, [5, 6]):
                    moves.append((row, 6))
                if castling_rights.get(f"{self.color}_queenside") and self._castle_path_is_clear(board, row, 0, [1, 2, 3]):
                    moves.append((row, 2))

        return moves

    def _castle_path_is_clear(self, board, row, rook_col, empty_cols):
        rook = self._get_piece(board, row, rook_col)
        if rook in (None, ".") or rook.type != "R" or rook.color != self.color:
            return False
        return all(self._is_empty(board, row, col) for col in empty_cols)


class Board:
    """Board state loaded from FEN and updated after successful moves."""

    PIECE_MAP = {
        "P": Pawn,
        "N": Knight,
        "B": Bishop,
        "R": Rook,
        "Q": Queen,
        "K": King,
    }

    def __init__(self):
        self.grid = [["." for _ in range(8)] for _ in range(8)]
        self.turn = "white"
        self.castling_rights = {
            "white_kingside": False,
            "white_queenside": False,
            "black_kingside": False,
            "black_queenside": False,
        }
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1

    @classmethod
    def from_fen(cls, fen_string):
        parts = fen_string.strip().split()
        if len(parts) < 4:
            raise ValueError("Invalid FEN string")

        board = cls()
        rows = parts[0].split("/")
        if len(rows) != 8:
            raise ValueError("Invalid FEN board layout")

        for row_index, row_str in enumerate(rows):
            col_index = 0
            for char in row_str:
                if char.isdigit():
                    count = int(char)
                    for _ in range(count):
                        board.grid[row_index][col_index] = "."
                        col_index += 1
                else:
                    color = "white" if char.isupper() else "black"
                    piece_type = char.upper()
                    board.grid[row_index][col_index] = cls.PIECE_MAP[piece_type](color)
                    col_index += 1
            if col_index != 8:
                raise ValueError("Invalid FEN row width")

        board.turn = "white" if parts[1] == "w" else "black"
        castling = parts[2]
        board.castling_rights = {
            "white_kingside": "K" in castling,
            "white_queenside": "Q" in castling,
            "black_kingside": "k" in castling,
            "black_queenside": "q" in castling,
        }

        board.en_passant_target = None if parts[3] == "-" else square_to_coords(parts[3])
        if len(parts) > 4:
            board.halfmove_clock = int(parts[4])
        if len(parts) > 5:
            board.fullmove_number = int(parts[5])

        board._sync_special_move_flags()
        return board

    @classmethod
    def load_from_file(cls, filename):
        with open(filename, "r", encoding="utf-8") as handle:
            return cls.from_fen(handle.read().strip())

    def copy(self):
        new_board = Board()
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece != ".":
                    new_piece = type(piece)(piece.color)
                    new_piece.has_moved = piece.has_moved
                    new_board.grid[row][col] = new_piece
        new_board.turn = self.turn
        new_board.castling_rights = self.castling_rights.copy()
        new_board.en_passant_target = self.en_passant_target
        new_board.halfmove_clock = self.halfmove_clock
        new_board.fullmove_number = self.fullmove_number
        return new_board

    def get_piece(self, row, col):
        if 0 <= row <= 7 and 0 <= col <= 7:
            return self.grid[row][col]
        return None

    def set_piece(self, row, col, piece):
        self.grid[row][col] = piece

    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece != "." and piece.type == "K" and piece.color == color:
                    return (row, col)
        return None

    def display(self):
        lines = ["  a b c d e f g h", "  ---------------"]
        for row_index, row in enumerate(self.grid):
            rank = 8 - row_index
            display_row = []
            for cell in row:
                if cell == ".":
                    display_row.append(".")
                else:
                    display_row.append(piece_symbol(cell.type, cell.color))
            lines.append(f"{rank}|{' '.join(display_row)}|{rank}")
        lines.append("  ---------------")
        lines.append("  a b c d e f g h")
        return "\n".join(lines)

    def apply_move(self, from_coords, to_coords):
        from_row, from_col = from_coords
        to_row, to_col = to_coords
        piece = self.get_piece(from_row, from_col)
        captured_piece, captured_coords = self._get_capture_info(from_coords, to_coords, piece)
        moving_piece_type = piece.type

        self._update_castling_rights(from_coords, piece, captured_piece, captured_coords)

        if moving_piece_type == "P" and (to_row, to_col) == self.en_passant_target and self.get_piece(to_row, to_col) == ".":
            self.set_piece(from_row, to_col, ".")

        self.set_piece(to_row, to_col, piece)
        self.set_piece(from_row, from_col, ".")
        piece.has_moved = True

        if moving_piece_type == "K" and abs(to_col - from_col) == 2:
            if to_col > from_col:
                rook = self.get_piece(from_row, 7)
                self.set_piece(from_row, 5, rook)
                self.set_piece(from_row, 7, ".")
            else:
                rook = self.get_piece(from_row, 0)
                self.set_piece(from_row, 3, rook)
                self.set_piece(from_row, 0, ".")
            rook.has_moved = True

        if moving_piece_type == "P" and (to_row == 0 or to_row == 7):
            promoted = Queen(piece.color)
            promoted.has_moved = True
            self.set_piece(to_row, to_col, promoted)

        if moving_piece_type == "P" and abs(to_row - from_row) == 2:
            self.en_passant_target = ((from_row + to_row) // 2, from_col)
        else:
            self.en_passant_target = None

        if moving_piece_type == "P" or captured_piece is not None:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        self.turn = "black" if self.turn == "white" else "white"
        if self.turn == "white":
            self.fullmove_number += 1

    def _sync_special_move_flags(self):
        for color, home_row in (("white", 7), ("black", 0)):
            king = self.get_piece(home_row, 4)
            rook_a = self.get_piece(home_row, 0)
            rook_h = self.get_piece(home_row, 7)
            can_king = self.castling_rights.get(f"{color}_kingside", False)
            can_queen = self.castling_rights.get(f"{color}_queenside", False)

            if king != "." and king is not None and king.type == "K" and king.color == color:
                king.has_moved = not (can_king or can_queen)
            if rook_h != "." and rook_h is not None and rook_h.type == "R" and rook_h.color == color:
                rook_h.has_moved = not can_king
            if rook_a != "." and rook_a is not None and rook_a.type == "R" and rook_a.color == color:
                rook_a.has_moved = not can_queen

    def _get_capture_info(self, from_coords, to_coords, piece):
        from_row, _ = from_coords
        to_row, to_col = to_coords
        if piece.type == "P" and (to_row, to_col) == self.en_passant_target and self.get_piece(to_row, to_col) == ".":
            captured_coords = (from_row, to_col)
        else:
            captured_coords = to_coords
        captured_piece = self.get_piece(*captured_coords)
        if captured_piece == ".":
            captured_piece = None
        return captured_piece, captured_coords

    def _update_castling_rights(self, from_coords, piece, captured_piece=None, captured_coords=None):
        if piece.type == "K":
            self.castling_rights[f"{piece.color}_kingside"] = False
            self.castling_rights[f"{piece.color}_queenside"] = False

        if piece.type == "R":
            if from_coords == (7, 0) and piece.color == "white":
                self.castling_rights["white_queenside"] = False
            elif from_coords == (7, 7) and piece.color == "white":
                self.castling_rights["white_kingside"] = False
            elif from_coords == (0, 0) and piece.color == "black":
                self.castling_rights["black_queenside"] = False
            elif from_coords == (0, 7) and piece.color == "black":
                self.castling_rights["black_kingside"] = False

        if captured_piece is not None and captured_piece.type == "R":
            if captured_piece.color == "white" and captured_coords == (7, 0):
                self.castling_rights["white_queenside"] = False
            elif captured_piece.color == "white" and captured_coords == (7, 7):
                self.castling_rights["white_kingside"] = False
            elif captured_piece.color == "black" and captured_coords == (0, 0):
                self.castling_rights["black_queenside"] = False
            elif captured_piece.color == "black" and captured_coords == (0, 7):
                self.castling_rights["black_kingside"] = False


class MoveValidator:
    """DFA move validator with trace output and king-safety simulation."""

    def __init__(self, board):
        self.board = board
        self.last_reject_reason = None

    def validate(self, move_str):
        """Validate a move string through S0..S4."""
        trace = []
        self.last_reject_reason = None

        # S0: Parse the raw move string into source and destination squares.
        parsed = parse_move_input(move_str)
        if parsed is None:
            self.last_reject_reason = "Invalid move format"
            trace.append(("✗", STATE_LABELS[0], f'invalid move string "{move_str.strip()}"'))
            self._append_skipped(trace, 1)
            return False, trace, "Error E001: Invalid format. Use 'e2e4' or 'e2-e4'"

        from_coords, to_coords = parsed
        from_sq = coords_to_square(*from_coords)
        to_sq = coords_to_square(*to_coords)
        trace.append(("✓", STATE_LABELS[0], f'"{move_str.strip()}" parsed'))

        # S1: Confirm both coordinates are still within the 8x8 board.
        if not self._in_bounds(from_coords) or not self._in_bounds(to_coords):
            self.last_reject_reason = "Out of bounds move"
            trace.append(("✗", STATE_LABELS[1], f"{from_sq} or {to_sq} is outside the board"))
            self._append_skipped(trace, 2)
            return False, trace, "Error E001: Invalid format. Use 'e2e4' or 'e2-e4'"

        trace.append(("✓", STATE_LABELS[1], f"{from_sq} ∈ board, {to_sq} ∈ board"))

        # S2: The source square must contain a piece of the active color.
        piece = self.board.get_piece(*from_coords)
        if piece == ".":
            self.last_reject_reason = "Source square empty"
            trace.append(("✗", STATE_LABELS[2], f"no piece at {from_sq}"))
            self._append_skipped(trace, 3)
            return False, trace, f"Error E002: No piece at {from_sq}. Square is empty."

        if piece.color != self.board.turn:
            self.last_reject_reason = "Wrong color piece"
            trace.append(("✗", STATE_LABELS[2], f"{piece_title(piece)} at {from_sq}, but {self.board.turn} to move"))
            self._append_skipped(trace, 3)
            return False, trace, f"Error E003: Piece at {from_sq} is {piece.color}, but it's {self.board.turn}'s turn"

        trace.append(("✓", STATE_LABELS[2], f"{piece_title(piece)} at {from_sq}"))

        # S3: Apply deterministic piece-movement rules and special-move rules.
        rules_ok, success_msg, reject_reason, error_msg = self._validate_rules(from_coords, to_coords, piece)
        if not rules_ok:
            self.last_reject_reason = reject_reason
            trace.append(("✗", STATE_LABELS[3], success_msg))
            self._append_skipped(trace, 4)
            return False, trace, error_msg

        trace.append(("✓", STATE_LABELS[3], success_msg))

        # S4: Simulate the move and reject it if the moving side's king is unsafe.
        if self._would_leave_king_in_check(from_coords, to_coords, piece):
            self.last_reject_reason = "King would be in check"
            trace.append(("✗", STATE_LABELS[4], "king would be in check after move"))
            return False, trace, "Error E006: Illegal: Your king would be in check after this move"

        trace.append(("✓", STATE_LABELS[4], "King safe after move"))
        return True, trace, None

    def is_valid_move(self, from_coords, to_coords):
        """Compatibility helper for programmatic move validation."""
        if not self._in_bounds(from_coords) or not self._in_bounds(to_coords):
            return False

        piece = self.board.get_piece(*from_coords)
        if piece == "." or piece.color != self.board.turn:
            return False

        rules_ok, _, _, _ = self._validate_rules(from_coords, to_coords, piece)
        if not rules_ok:
            return False

        return not self._would_leave_king_in_check(from_coords, to_coords, piece)

    def simulate_move(self, from_sq, to_sq):
        """Return a copied board with the move applied."""
        from_coords = square_to_coords(from_sq) if isinstance(from_sq, str) else from_sq
        to_coords = square_to_coords(to_sq) if isinstance(to_sq, str) else to_sq
        temp_board = self.board.copy()
        self._apply_move_on_board(temp_board, from_coords, to_coords)
        return temp_board

    def is_king_in_check(self, board, color):
        king_pos = board.find_king(color)
        if king_pos is None:
            return False
        return self._is_square_attacked(board, king_pos[0], king_pos[1], color)

    def is_in_check(self, color):
        return self.is_king_in_check(self.board, color)

    def has_any_legal_moves(self, color):
        original_turn = self.board.turn
        self.board.turn = color
        try:
            for row in range(8):
                for col in range(8):
                    piece = self.board.get_piece(row, col)
                    if piece != "." and piece.color == color:
                        for move in piece.get_possible_moves(row, col, self.board):
                            if self.is_valid_move((row, col), move):
                                return True
            return False
        finally:
            self.board.turn = original_turn

    def get_all_legal_moves(self, color):
        original_turn = self.board.turn
        self.board.turn = color
        try:
            legal_moves = []
            for row in range(8):
                for col in range(8):
                    piece = self.board.get_piece(row, col)
                    if piece != "." and piece.color == color:
                        for move in piece.get_possible_moves(row, col, self.board):
                            if self.is_valid_move((row, col), move):
                                legal_moves.append(((row, col), move))
            return legal_moves
        finally:
            self.board.turn = original_turn

    def _validate_rules(self, from_coords, to_coords, piece):
        from_row, from_col = from_coords
        to_row, to_col = to_coords
        from_sq = coords_to_square(*from_coords)
        to_sq = coords_to_square(*to_coords)
        target_piece = self.board.get_piece(to_row, to_col)

        if target_piece != "." and target_piece.color == piece.color:
            return False, f"cannot capture own piece on {to_sq}", "Destination has own piece", f"Error E007: Cannot capture your own piece at {to_sq}"

        if piece.type == "P":
            return self._validate_pawn_move(from_coords, to_coords, piece)
        if piece.type == "N":
            delta_row = abs(to_row - from_row)
            delta_col = abs(to_col - from_col)
            if (delta_row, delta_col) == (1, 2) or (delta_row, delta_col) == (2, 1):
                return True, f"Knight moves {from_sq}→{to_sq} ✓", None, None
            return False, f"Knight cannot move {from_sq}→{to_sq}", "Illegal Knight movement", f"Error E004: Knight cannot move from {from_sq} to {to_sq}"
        if piece.type == "B":
            return self._validate_slider_move(from_coords, to_coords, piece, abs(to_row - from_row) == abs(to_col - from_col))
        if piece.type == "R":
            return self._validate_slider_move(from_coords, to_coords, piece, from_row == to_row or from_col == to_col)
        if piece.type == "Q":
            is_straight = from_row == to_row or from_col == to_col
            is_diagonal = abs(to_row - from_row) == abs(to_col - from_col)
            return self._validate_slider_move(from_coords, to_coords, piece, is_straight or is_diagonal)
        if piece.type == "K":
            return self._validate_king_move(from_coords, to_coords, piece)

        return False, f"unsupported piece move {from_sq}→{to_sq}", "Illegal movement", f"Error E004: {PIECE_NAMES[piece.type]} cannot move from {from_sq} to {to_sq}"

    def _validate_pawn_move(self, from_coords, to_coords, piece):
        from_row, from_col = from_coords
        to_row, to_col = to_coords
        from_sq = coords_to_square(*from_coords)
        to_sq = coords_to_square(*to_coords)
        target_piece = self.board.get_piece(to_row, to_col)
        start_row = 6 if piece.color == "white" else 1
        delta_row = to_row - from_row
        delta_col = to_col - from_col
        direction = -1 if piece.color == "white" else 1

        if delta_col == 0:
            if delta_row == direction:
                if target_piece == ".":
                    return True, f"Pawn moves {from_sq}→{to_sq} ✓", None, None
                blocker_sq = to_sq
                return False, f"path blocked to {to_sq}", "Path blocked", f"Error E005: Path from {from_sq} to {to_sq} is blocked by {piece_title(target_piece)} at {blocker_sq}"
            if delta_row == 2 * direction and from_row == start_row:
                mid_row = from_row + direction
                mid_piece = self.board.get_piece(mid_row, from_col)
                if mid_piece != ".":
                    blocker_sq = coords_to_square(mid_row, from_col)
                    return False, f"path blocked at {blocker_sq}", "Path blocked", f"Error E005: Path from {from_sq} to {to_sq} is blocked by {piece_title(mid_piece)} at {blocker_sq}"
                if target_piece != ".":
                    return False, f"path blocked to {to_sq}", "Path blocked", f"Error E005: Path from {from_sq} to {to_sq} is blocked by {piece_title(target_piece)} at {to_sq}"
                return True, f"Pawn moves {from_sq}→{to_sq} ✓", None, None
            return False, f"Pawn cannot move {from_sq}→{to_sq}", "Illegal Pawn movement", f"Error E004: Pawn cannot move from {from_sq} to {to_sq}"

        if abs(delta_col) == 1 and delta_row == direction:
            if target_piece != "." and target_piece.color != piece.color:
                return True, f"Pawn captures {from_sq}→{to_sq} ✓", None, None
            if (to_row, to_col) == self.board.en_passant_target:
                captured_pawn = self.board.get_piece(from_row, to_col)
                if captured_pawn != "." and captured_pawn.type == "P" and captured_pawn.color != piece.color:
                    return True, f"Pawn captures en passant {from_sq}→{to_sq} ✓", None, None
            return False, f"Pawn cannot move {from_sq}→{to_sq}", "Illegal Pawn movement", f"Error E004: Pawn cannot move from {from_sq} to {to_sq}"

        return False, f"Pawn cannot move {from_sq}→{to_sq}", "Illegal Pawn movement", f"Error E004: Pawn cannot move from {from_sq} to {to_sq}"

    def _validate_slider_move(self, from_coords, to_coords, piece, shape_ok):
        from_row, from_col = from_coords
        to_row, to_col = to_coords
        from_sq = coords_to_square(*from_coords)
        to_sq = coords_to_square(*to_coords)

        if not shape_ok:
            return False, f"{PIECE_NAMES[piece.type]} cannot move {from_sq}→{to_sq}", f"Illegal {PIECE_NAMES[piece.type]} movement", f"Error E004: {PIECE_NAMES[piece.type]} cannot move from {from_sq} to {to_sq}"

        blocker = self._find_blocker(from_coords, to_coords)
        if blocker is not None:
            blocker_sq = coords_to_square(*blocker)
            blocker_piece = self.board.get_piece(*blocker)
            return False, f"path blocked at {blocker_sq}", "Path blocked", f"Error E005: Path from {from_sq} to {to_sq} is blocked by {piece_title(blocker_piece)} at {blocker_sq}"

        return True, f"{PIECE_NAMES[piece.type]} moves {from_sq}→{to_sq} ✓", None, None

    def _validate_king_move(self, from_coords, to_coords, piece):
        from_row, from_col = from_coords
        to_row, to_col = to_coords
        from_sq = coords_to_square(*from_coords)
        to_sq = coords_to_square(*to_coords)
        delta_row = abs(to_row - from_row)
        delta_col = abs(to_col - from_col)

        if max(delta_row, delta_col) == 1:
            return True, f"King moves {from_sq}→{to_sq} ✓", None, None

        if delta_row == 0 and delta_col == 2:
            rights_key = f"{piece.color}_kingside" if to_col > from_col else f"{piece.color}_queenside"
            rook_col = 7 if to_col > from_col else 0
            rook = self.board.get_piece(from_row, rook_col)
            if not self.board.castling_rights.get(rights_key, False):
                return False, f"castling not available {from_sq}→{to_sq}", "Illegal castling", f"Error E004: King cannot move from {from_sq} to {to_sq}"
            if rook == "." or rook.type != "R" or rook.color != piece.color or rook.has_moved:
                return False, f"rook unavailable for castling", "Illegal castling", f"Error E004: King cannot move from {from_sq} to {to_sq}"
            blocker = self._find_blocker(from_coords, (from_row, rook_col))
            if blocker is not None:
                blocker_sq = coords_to_square(*blocker)
                blocker_piece = self.board.get_piece(*blocker)
                return False, f"path blocked at {blocker_sq}", "Path blocked", f"Error E005: Path from {from_sq} to {to_sq} is blocked by {piece_title(blocker_piece)} at {blocker_sq}"
            return True, f"King castles {from_sq}→{to_sq} ✓", None, None

        return False, f"King cannot move {from_sq}→{to_sq}", "Illegal King movement", f"Error E004: King cannot move from {from_sq} to {to_sq}"

    def _find_blocker(self, from_coords, to_coords):
        from_row, from_col = from_coords
        to_row, to_col = to_coords
        step_row = 0 if to_row == from_row else (1 if to_row > from_row else -1)
        step_col = 0 if to_col == from_col else (1 if to_col > from_col else -1)

        cur_row = from_row + step_row
        cur_col = from_col + step_col
        while (cur_row, cur_col) != (to_row, to_col):
            if self.board.get_piece(cur_row, cur_col) != ".":
                return (cur_row, cur_col)
            cur_row += step_row
            cur_col += step_col
        return None

    def _would_leave_king_in_check(self, from_coords, to_coords, piece):
        from_row, from_col = from_coords
        to_row, to_col = to_coords

        if piece.type == "K" and abs(to_col - from_col) == 2:
            step = 1 if to_col > from_col else -1
            if self._is_square_attacked(self.board, from_row, from_col, piece.color):
                return True
            if self._is_square_attacked(self.board, from_row, from_col + step, piece.color):
                return True

        temp_board = self.board.copy()
        self._apply_move_on_board(temp_board, from_coords, to_coords)
        return self.is_king_in_check(temp_board, piece.color)

    def _is_square_attacked(self, board, row, col, defending_color):
        enemy_color = "black" if defending_color == "white" else "white"
        for enemy_row in range(8):
            for enemy_col in range(8):
                piece = board.get_piece(enemy_row, enemy_col)
                if piece == "." or piece.color != enemy_color:
                    continue
                if piece.type == "P":
                    direction = -1 if piece.color == "white" else 1
                    if (row, col) in ((enemy_row + direction, enemy_col - 1), (enemy_row + direction, enemy_col + 1)):
                        return True
                    continue
                if piece.type == "K":
                    if max(abs(row - enemy_row), abs(col - enemy_col)) == 1:
                        return True
                    continue
                if (row, col) in piece.get_possible_moves(enemy_row, enemy_col, board):
                    return True
        return False

    def _append_skipped(self, trace, start_index):
        for index in range(start_index, len(STATE_LABELS)):
            trace.append(("—", STATE_LABELS[index], "(skipped)"))

    def _in_bounds(self, coords):
        row, col = coords
        return 0 <= row <= 7 and 0 <= col <= 7

    def _apply_move_on_board(self, board, from_coords, to_coords):
        """Apply a move to any compatible board object."""
        from_row, from_col = from_coords
        to_row, to_col = to_coords
        piece = board.get_piece(from_row, from_col)
        captured_piece, captured_coords = self._get_capture_info_on_board(board, from_coords, to_coords, piece)
        moving_piece_type = piece.type

        self._update_castling_rights_on_board(board, from_coords, piece, captured_piece, captured_coords)

        if moving_piece_type == "P" and (to_row, to_col) == board.en_passant_target and board.get_piece(to_row, to_col) == ".":
            board.set_piece(from_row, to_col, ".")

        board.set_piece(to_row, to_col, piece)
        board.set_piece(from_row, from_col, ".")
        piece.has_moved = True

        if moving_piece_type == "K" and abs(to_col - from_col) == 2:
            if to_col > from_col:
                rook = board.get_piece(from_row, 7)
                board.set_piece(from_row, 5, rook)
                board.set_piece(from_row, 7, ".")
            else:
                rook = board.get_piece(from_row, 0)
                board.set_piece(from_row, 3, rook)
                board.set_piece(from_row, 0, ".")
            rook.has_moved = True

        if moving_piece_type == "P" and (to_row == 0 or to_row == 7):
            promoted = Queen(piece.color)
            promoted.has_moved = True
            board.set_piece(to_row, to_col, promoted)

        if moving_piece_type == "P" and abs(to_row - from_row) == 2:
            board.en_passant_target = ((from_row + to_row) // 2, from_col)
        else:
            board.en_passant_target = None

        if moving_piece_type == "P" or captured_piece is not None:
            board.halfmove_clock = 0
        else:
            board.halfmove_clock += 1

        board.turn = "black" if board.turn == "white" else "white"
        if board.turn == "white":
            board.fullmove_number += 1

    def _get_capture_info_on_board(self, board, from_coords, to_coords, piece):
        from_row, _ = from_coords
        to_row, to_col = to_coords
        if piece.type == "P" and (to_row, to_col) == board.en_passant_target and board.get_piece(to_row, to_col) == ".":
            captured_coords = (from_row, to_col)
        else:
            captured_coords = to_coords
        captured_piece = board.get_piece(*captured_coords)
        if captured_piece == ".":
            captured_piece = None
        return captured_piece, captured_coords

    def _update_castling_rights_on_board(self, board, from_coords, piece, captured_piece=None, captured_coords=None):
        if piece.type == "K":
            board.castling_rights[f"{piece.color}_kingside"] = False
            board.castling_rights[f"{piece.color}_queenside"] = False

        if piece.type == "R":
            if from_coords == (7, 0) and piece.color == "white":
                board.castling_rights["white_queenside"] = False
            elif from_coords == (7, 7) and piece.color == "white":
                board.castling_rights["white_kingside"] = False
            elif from_coords == (0, 0) and piece.color == "black":
                board.castling_rights["black_queenside"] = False
            elif from_coords == (0, 7) and piece.color == "black":
                board.castling_rights["black_kingside"] = False

        if captured_piece is not None and captured_piece.type == "R":
            if captured_piece.color == "white" and captured_coords == (7, 0):
                board.castling_rights["white_queenside"] = False
            elif captured_piece.color == "white" and captured_coords == (7, 7):
                board.castling_rights["white_kingside"] = False
            elif captured_piece.color == "black" and captured_coords == (0, 0):
                board.castling_rights["black_queenside"] = False
            elif captured_piece.color == "black" and captured_coords == (0, 7):
                board.castling_rights["black_kingside"] = False


def render_trace(trace, accepted, reject_reason=None, error_msg=None):
    """Render a boxed DFA trace."""
    body_lines = [f"  [{status}] {state:<10}: {message}" for status, state, message in trace]

    if accepted:
        footer_lines = ["  ✓ ACCEPT — Move is LEGAL"]
    else:
        headline = reject_reason or "Move rejected"
        footer_lines = [f"  ✗ REJECT — {headline}"]
        if error_msg:
            wrapped = textwrap.wrap(error_msg, width=56)
            footer_lines.extend([f"    {line}" for line in wrapped])

    title = "DFA MOVE VALIDATION TRACE"
    inner_width = max(41, len(title) + 2, *(len(line) for line in body_lines + footer_lines))

    top = "┌" + ("─" * inner_width) + "┐"
    header = "│" + title.center(inner_width) + "│"
    divider = "├" + ("─" * inner_width) + "┤"
    bottom = "└" + ("─" * inner_width) + "┘"

    rendered = [top, header, divider]
    rendered.extend("│" + line.ljust(inner_width) + "│" for line in body_lines)
    rendered.append(divider)
    rendered.extend("│" + line.ljust(inner_width) + "│" for line in footer_lines)
    rendered.append(bottom)
    return "\n".join(rendered)


def normalize_trace(trace):
    """Normalize trace rows so every DFA state has a display entry."""
    trace_map = {state: (status, message) for status, state, message in trace}
    normalized = []
    for state in STATE_LABELS:
        status, message = trace_map.get(state, ("—", "Awaiting traversal"))
        normalized.append((status, state, message))
    return normalized


def summary_text(accepted, reject_reason=None, error_msg=None):
    """Build a concise result summary for CLI and GUI surfaces."""
    if accepted:
        return "ACCEPT — Move is legal."
    parts = [f"REJECT — {reject_reason or 'Move rejected'}"]
    if error_msg:
        parts.append(error_msg)
    return "\n".join(parts)


def print_turn_prompt(board):
    print(f"\n{board.turn.capitalize()} to move.")


def load_board_or_exit(fen_path):
    """Load a board from FEN and exit with a friendly error on failure."""
    try:
        return Board.load_from_file(fen_path)
    except FileNotFoundError:
        print(f"Could not open FEN file: {fen_path}")
        return None
    except ValueError as exc:
        print(f"Failed to parse FEN file {fen_path}: {exc}")
        return None


def run_cli(fen_path):
    board = load_board_or_exit(fen_path)
    if board is None:
        return 1

    print(f"Loaded position from {fen_path}")
    print(board.display())
    print_turn_prompt(board)

    while True:
        try:
            user_input = input("Enter move (e.g., e2e4) or 'quit': ").strip()
        except EOFError:
            print("\nExiting DFA Move Validator.")
            return 0

        if user_input.lower() == "quit":
            print("Exiting DFA Move Validator.")
            return 0

        validator = MoveValidator(board)
        is_valid, trace, error_msg = validator.validate(user_input)
        print()
        print(render_trace(trace, is_valid, validator.last_reject_reason, error_msg))

        if not is_valid:
            print("\nMove rejected. Board unchanged.")
            print_turn_prompt(board)
            continue

        parsed = parse_move_input(user_input)
        board.apply_move(*parsed)
        print("\nUpdated board:")
        print(board.display())
        print_turn_prompt(board)


class DfaTraversalApp:
    """Tkinter GUI for board state, move input, and DFA traversal."""

    BOARD_LIGHT = "#efe6d5"
    BOARD_DARK = "#8a6f4d"
    PANEL_BG = "#f6f0e5"
    PANEL_ALT = "#fffaf1"
    TEXT_DARK = "#2f2417"
    TEXT_MUTED = "#72614d"
    STATUS_COLORS = {"✓": "#2e7d32", "✗": "#b3261e", "—": "#90a4ae"}

    def __init__(self, root, board, fen_path):
        self.root = root
        self.board = board
        self.fen_path = fen_path
        self.square_labels = {}
        self.trace_rows = []
        self.current_trace = normalize_trace([])
        self.last_move = None

        self._build_ui()
        self.refresh_board()
        self.update_trace_ui(self.current_trace, None)
        self.update_turn_banner()

    def _build_ui(self):
        self.root.title("DFA Move Validator")
        self.root.configure(bg=self.PANEL_BG)
        self.root.geometry("1040x680")
        self.root.minsize(980, 620)

        outer = tk.Frame(self.root, bg=self.PANEL_BG, padx=12, pady=12)
        outer.pack(fill="both", expand=True)

        header = tk.Frame(outer, bg=self.PANEL_BG)
        header.pack(fill="x", pady=(0, 10))

        title = tk.Label(
            header,
            text="Deterministic Finite Automaton Chess Validator",
            font=("Georgia", 20, "bold"),
            bg=self.PANEL_BG,
            fg=self.TEXT_DARK,
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text=f"Loaded from {self.fen_path} | Enter moves like e2e4 or e2-e4",
            font=("Helvetica", 10),
            bg=self.PANEL_BG,
            fg=self.TEXT_MUTED,
        )
        subtitle.pack(anchor="w", pady=(4, 0))

        self.turn_banner = tk.Label(
            header,
            text="",
            font=("Helvetica", 11, "bold"),
            bg="#1f4b3f",
            fg="#f8f5ef",
            padx=12,
            pady=6,
        )
        self.turn_banner.pack(anchor="e", pady=(6, 0))

        body = tk.Frame(outer, bg=self.PANEL_BG)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        board_panel = tk.Frame(body, bg=self.PANEL_ALT, padx=12, pady=12, bd=1, relief="solid")
        board_panel.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        board_title = tk.Label(
            board_panel,
            text="Board",
            font=("Georgia", 16, "bold"),
            bg=self.PANEL_ALT,
            fg=self.TEXT_DARK,
        )
        board_title.grid(row=0, column=0, columnspan=10, sticky="w", pady=(0, 8))

        self._build_board_grid(board_panel)

        controls = tk.Frame(body, bg=self.PANEL_BG)
        controls.grid(row=0, column=1, sticky="nsew")
        controls.grid_columnconfigure(0, weight=1)
        controls.grid_rowconfigure(4, weight=1)

        input_panel = tk.Frame(controls, bg=self.PANEL_ALT, padx=12, pady=12, bd=1, relief="solid")
        input_panel.grid(row=0, column=0, sticky="ew")
        input_panel.grid_columnconfigure(1, weight=1)

        tk.Label(
            input_panel,
            text="Move Input",
            font=("Georgia", 15, "bold"),
            bg=self.PANEL_ALT,
            fg=self.TEXT_DARK,
        ).grid(row=0, column=0, columnspan=4, sticky="w")

        tk.Label(
            input_panel,
            text="Enter move:",
            font=("Helvetica", 10),
            bg=self.PANEL_ALT,
            fg=self.TEXT_MUTED,
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

        self.move_var = tk.StringVar()
        self.move_entry = tk.Entry(
            input_panel,
            textvariable=self.move_var,
            font=("Consolas", 13),
            width=16,
            relief="solid",
            bd=1,
        )
        self.move_entry.grid(row=1, column=1, sticky="ew", padx=(8, 8), pady=(8, 0))
        self.move_entry.bind("<Return>", self.submit_move)

        submit_button = tk.Button(
            input_panel,
            text="Validate Move",
            font=("Helvetica", 10, "bold"),
            bg="#244f43",
            fg="#f8f5ef",
            activebackground="#2c6455",
            activeforeground="#f8f5ef",
            padx=10,
            pady=6,
            command=self.submit_move,
            relief="flat",
        )
        submit_button.grid(row=1, column=2, sticky="ew", pady=(8, 0))

        reset_button = tk.Button(
            input_panel,
            text="Reset Position",
            font=("Helvetica", 10),
            bg="#d8c9ab",
            fg=self.TEXT_DARK,
            activebackground="#ccb996",
            padx=10,
            pady=6,
            command=self.reset_position,
            relief="flat",
        )
        reset_button.grid(row=1, column=3, sticky="ew", padx=(8, 0), pady=(8, 0))

        self.summary_label = tk.Label(
            input_panel,
            text="Awaiting your first move.",
            font=("Helvetica", 10),
            bg=self.PANEL_ALT,
            fg=self.TEXT_DARK,
            justify="left",
            wraplength=520,
        )
        self.summary_label.grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0))

        stepper_panel = tk.Frame(controls, bg=self.PANEL_ALT, padx=12, pady=12, bd=1, relief="solid")
        stepper_panel.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        tk.Label(
            stepper_panel,
            text="DFA Traversal",
            font=("Georgia", 15, "bold"),
            bg=self.PANEL_ALT,
            fg=self.TEXT_DARK,
        ).pack(anchor="w")

        self.stepper_canvas = tk.Canvas(
            stepper_panel,
            width=620,
            height=100,
            bg=self.PANEL_ALT,
            highlightthickness=0,
        )
        self.stepper_canvas.pack(fill="x", pady=(8, 0))

        trace_panel = tk.Frame(controls, bg=self.PANEL_ALT, padx=12, pady=12, bd=1, relief="solid")
        trace_panel.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        tk.Label(
            trace_panel,
            text="State Details",
            font=("Georgia", 15, "bold"),
            bg=self.PANEL_ALT,
            fg=self.TEXT_DARK,
        ).pack(anchor="w")

        self.trace_rows_frame = tk.Frame(trace_panel, bg=self.PANEL_ALT)
        self.trace_rows_frame.pack(fill="x", pady=(8, 0))
        self._build_trace_rows()

        rendered_panel = tk.Frame(controls, bg=self.PANEL_ALT, padx=12, pady=12, bd=1, relief="solid")
        rendered_panel.grid(row=3, column=0, sticky="nsew", pady=(12, 0))
        rendered_panel.grid_columnconfigure(0, weight=1)
        rendered_panel.grid_rowconfigure(1, weight=1)

        tk.Label(
            rendered_panel,
            text="Rendered Trace",
            font=("Georgia", 15, "bold"),
            bg=self.PANEL_ALT,
            fg=self.TEXT_DARK,
        ).grid(row=0, column=0, sticky="w")

        self.trace_text = tk.Text(
            rendered_panel,
            font=("Consolas", 10),
            height=12,
            bg="#fcfaf4",
            fg=self.TEXT_DARK,
            relief="solid",
            bd=1,
            wrap="word",
            padx=8,
            pady=8,
        )
        self.trace_text.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.trace_text.configure(state="disabled")

        history_panel = tk.Frame(controls, bg=self.PANEL_ALT, padx=12, pady=12, bd=1, relief="solid")
        history_panel.grid(row=4, column=0, sticky="nsew", pady=(12, 0))
        history_panel.grid_columnconfigure(0, weight=1)
        history_panel.grid_rowconfigure(1, weight=1)

        tk.Label(
            history_panel,
            text="Move History",
            font=("Georgia", 15, "bold"),
            bg=self.PANEL_ALT,
            fg=self.TEXT_DARK,
        ).grid(row=0, column=0, sticky="w")

        self.history_list = tk.Listbox(
            history_panel,
            font=("Consolas", 10),
            height=6,
            bg="#fcfaf4",
            fg=self.TEXT_DARK,
            relief="solid",
            bd=1,
            activestyle="none",
        )
        self.history_list.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        self.move_entry.focus_set()

    def _build_board_grid(self, parent):
        board_frame = tk.Frame(parent, bg=self.PANEL_ALT)
        board_frame.grid(row=1, column=0, columnspan=10)

        for col in range(8):
            tk.Label(
                board_frame,
                text=chr(ord("a") + col),
                font=("Helvetica", 10, "bold"),
                bg=self.PANEL_ALT,
                fg=self.TEXT_MUTED,
                width=3,
            ).grid(row=0, column=col + 1, pady=(0, 6))

        for row in range(8):
            rank = 8 - row
            tk.Label(
                board_frame,
                text=str(rank),
                font=("Helvetica", 10, "bold"),
                bg=self.PANEL_ALT,
                fg=self.TEXT_MUTED,
                width=2,
            ).grid(row=row + 1, column=0, padx=(0, 6))

            for col in range(8):
                square = tk.Label(
                    board_frame,
                    text="",
                    font=("DejaVu Sans", 24),
                    width=2,
                    height=1,
                    bd=0,
                    relief="flat",
                )
                square.grid(row=row + 1, column=col + 1, ipadx=5, ipady=5)
                self.square_labels[(row, col)] = square

            tk.Label(
                board_frame,
                text=str(rank),
                font=("Helvetica", 10, "bold"),
                bg=self.PANEL_ALT,
                fg=self.TEXT_MUTED,
                width=2,
            ).grid(row=row + 1, column=9, padx=(6, 0))

        for col in range(8):
            tk.Label(
                board_frame,
                text=chr(ord("a") + col),
                font=("Helvetica", 10, "bold"),
                bg=self.PANEL_ALT,
                fg=self.TEXT_MUTED,
                width=3,
            ).grid(row=9, column=col + 1, pady=(6, 0))

    def _build_trace_rows(self):
        for index, state in enumerate(STATE_LABELS):
            row_bg = self.PANEL_ALT if index % 2 == 0 else "#faf4e8"
            row_frame = tk.Frame(self.trace_rows_frame, bg=row_bg, padx=8, pady=6)
            row_frame.pack(fill="x", pady=1)

            status_label = tk.Label(
                row_frame,
                text="—",
                font=("Helvetica", 13, "bold"),
                width=3,
                bg=row_bg,
                fg=self.STATUS_COLORS["—"],
            )
            status_label.pack(side="left")

            state_label = tk.Label(
                row_frame,
                text=state,
                font=("Consolas", 10, "bold"),
                bg=row_bg,
                fg=self.TEXT_DARK,
                width=12,
                anchor="w",
            )
            state_label.pack(side="left")

            message_label = tk.Label(
                row_frame,
                text="Awaiting traversal",
                font=("Helvetica", 10),
                bg=row_bg,
                fg=self.TEXT_MUTED,
                anchor="w",
                justify="left",
                wraplength=420,
            )
            message_label.pack(side="left", fill="x", expand=True, padx=(8, 0))

            self.trace_rows.append((status_label, message_label))

    def refresh_board(self):
        for row in range(8):
            for col in range(8):
                cell = self.board.get_piece(row, col)
                label = self.square_labels[(row, col)]
                bg = self.BOARD_LIGHT if (row + col) % 2 == 0 else self.BOARD_DARK
                label.configure(bg=bg, fg="#1f1f1f")
                if cell == ".":
                    label.configure(text="")
                else:
                    label.configure(text=piece_symbol(cell.type, cell.color))

    def update_turn_banner(self):
        label = f"{self.board.turn.capitalize()} to move"
        if self.last_move:
            label = f"{label} | Last move: {self.last_move}"
        self.turn_banner.configure(text=label)

    def update_trace_ui(self, normalized_trace, summary):
        for (status_label, message_label), (status, _state, message) in zip(self.trace_rows, normalized_trace):
            status_label.configure(text=status, fg=self.STATUS_COLORS.get(status, self.TEXT_MUTED))
            message_label.configure(text=message)

        self.draw_dfa_stepper(normalized_trace)

        if summary is None:
            rendered = (
                "DFA traversal will appear here after you validate a move.\n\n"
                "States:\n"
                "  S0 INPUT   -> parse move string\n"
                "  S1 BOUNDS  -> verify board coordinates\n"
                "  S2 PIECE   -> confirm active piece ownership\n"
                "  S3 RULES   -> apply deterministic movement rules\n"
                "  S4 SAFETY  -> ensure king remains safe"
            )
        else:
            rendered = summary["rendered"]
            self.summary_label.configure(
                text=summary["text"],
                fg=summary["color"],
            )

        if summary is None:
            self.summary_label.configure(text="Awaiting your first move.", fg=self.TEXT_MUTED)

        self.trace_text.configure(state="normal")
        self.trace_text.delete("1.0", "end")
        self.trace_text.insert("1.0", rendered)
        self.trace_text.configure(state="disabled")

    def draw_dfa_stepper(self, normalized_trace):
        self.stepper_canvas.delete("all")
        width = int(self.stepper_canvas.cget("width"))
        height = int(self.stepper_canvas.cget("height"))
        margin = 54
        y = 42
        positions = []

        for index in range(len(STATE_LABELS)):
            if len(STATE_LABELS) == 1:
                x = width // 2
            else:
                x = margin + index * ((width - 2 * margin) / (len(STATE_LABELS) - 1))
            positions.append(x)

        for index in range(len(positions) - 1):
            next_status = normalized_trace[index + 1][0]
            line_color = self.STATUS_COLORS["—"]
            if next_status == "✓":
                line_color = self.STATUS_COLORS["✓"]
            elif next_status == "✗":
                line_color = self.STATUS_COLORS["✗"]
            self.stepper_canvas.create_line(
                positions[index] + 18,
                y,
                positions[index + 1] - 18,
                y,
                fill=line_color,
                width=4,
            )

        for x, (status, state, _message) in zip(positions, normalized_trace):
            fill = self.STATUS_COLORS.get(status, self.STATUS_COLORS["—"])
            self.stepper_canvas.create_oval(x - 18, y - 18, x + 18, y + 18, fill=fill, outline="")
            self.stepper_canvas.create_text(x, y, text=state.split()[0], fill="#ffffff", font=("Helvetica", 10, "bold"))
            self.stepper_canvas.create_text(x, y + 34, text=state.split()[1], fill=self.TEXT_DARK, font=("Helvetica", 10, "bold"))

    def submit_move(self, _event=None):
        user_input = self.move_var.get().strip()
        if not user_input:
            return

        if user_input.lower() == "quit":
            self.root.destroy()
            return

        validator = MoveValidator(self.board)
        is_valid, trace, error_msg = validator.validate(user_input)
        normalized_trace = normalize_trace(trace)
        summary = {
            "text": summary_text(is_valid, validator.last_reject_reason, error_msg),
            "color": self.STATUS_COLORS["✓"] if is_valid else self.STATUS_COLORS["✗"],
            "rendered": render_trace(trace, is_valid, validator.last_reject_reason, error_msg),
        }

        self.update_trace_ui(normalized_trace, summary)

        if not is_valid:
            self.move_entry.selection_range(0, "end")
            return

        parsed = parse_move_input(user_input)
        move_text = user_input.replace("-", "").lower()
        self.board.apply_move(*parsed)
        self.last_move = move_text
        self.history_list.insert("end", move_text)
        self.refresh_board()
        self.update_turn_banner()
        self.move_var.set("")
        self.move_entry.focus_set()

    def reset_position(self):
        board = load_board_or_exit(self.fen_path)
        if board is None:
            if messagebox is not None:
                messagebox.showerror("Reset Failed", f"Could not reload position from {self.fen_path}.")
            return
        self.board = board
        self.last_move = None
        self.history_list.delete(0, "end")
        self.refresh_board()
        self.update_turn_banner()
        self.update_trace_ui(normalize_trace([]), None)
        self.move_var.set("")
        self.move_entry.focus_set()


def run_gui(fen_path):
    global tk, messagebox

    try:
        import tkinter as tk  # type: ignore
        from tkinter import messagebox  # type: ignore
    except Exception as exc:
        print(f"Could not start GUI mode: {exc}")
        return 1

    board = load_board_or_exit(fen_path)
    if board is None:
        return 1

    try:
        root = tk.Tk()
    except Exception as exc:
        print(f"Could not open GUI window: {exc}")
        return 1

    DfaTraversalApp(root, board, fen_path)
    root.mainloop()
    return 0


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="DFA chess move validator")
    parser.add_argument("fen_path", nargs="?", default=DEFAULT_FEN_PATH, help="Path to a FEN file")
    parser.add_argument("--gui", action="store_true", help="Launch the Tkinter GUI")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.gui:
        return run_gui(args.fen_path)
    return run_cli(args.fen_path)


if __name__ == "__main__":
    raise SystemExit(main())
