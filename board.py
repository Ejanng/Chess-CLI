"""
board.py
Board state representation using 8x8 grid.
Implements FEN parsing and board initialization.
"""

# File: chess_automaton/board.py

from pieces import Pawn, Knight, Bishop, Rook, Queen, King

class Board:
    """
    Board represents the current state in our DFA.
    State = 8x8 grid configuration + metadata (castling rights, en passant, etc.)
    """
    
    def __init__(self):
        self.grid = [['.' for _ in range(8)] for _ in range(8)]
        self.turn = 'white'           # Current player (DFA current state indicator)
        self.castling_rights = {
            'white_kingside': True,
            'white_queenside': True,
            'black_kingside': True,
            'black_queenside': True
        }
        self.en_passant_target = None  # Square vulnerable to en passant
        self.halfmove_clock = 0        # For 50-move rule
        self.fullmove_number = 1       # Move counter
        self.move_history = []         # Stack for undo (PDA-like behavior)
    
    def setup_default(self):
        """Initialize standard chess starting position."""
        # Black pieces (row 0, 1)
        back_row_black = [Rook('black'), Knight('black'), Bishop('black'), Queen('black'),
                          King('black'), Bishop('black'), Knight('black'), Rook('black')]
        for c, piece in enumerate(back_row_black):
            self.grid[0][c] = piece
        
        for c in range(8):
            self.grid[1][c] = Pawn('black')
        
        # White pieces (row 6, 7)
        for c in range(8):
            self.grid[6][c] = Pawn('white')
        
        back_row_white = [Rook('white'), Knight('white'), Bishop('white'), Queen('white'),
                          King('white'), Bishop('white'), Knight('white'), Rook('white')]
        for c, piece in enumerate(back_row_white):
            self.grid[7][c] = piece
    
    def get_piece(self, row, col):
        """Get piece at position, returns '.' if empty."""
        if 0 <= row <= 7 and 0 <= col <= 7:
            return self.grid[row][col]
        return None
    
    def set_piece(self, row, col, piece):
        """Place piece at position."""
        self.grid[row][col] = piece
    
    def find_king(self, color):
        """Find king position for check detection."""
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece != '.' and piece.type == 'K' and piece.color == color:
                    return (r, c)
        return None
    
    def copy(self):
        """Create deep copy of board state (for DFA state exploration)."""
        new_board = Board()
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece != '.':
                    # Create new piece instance
                    new_piece = type(piece)(piece.color)
                    new_piece.has_moved = piece.has_moved
                    new_board.grid[r][c] = new_piece
        
        new_board.turn = self.turn
        new_board.castling_rights = self.castling_rights.copy()
        new_board.en_passant_target = self.en_passant_target
        new_board.halfmove_clock = self.halfmove_clock
        new_board.fullmove_number = self.fullmove_number
        return new_board
    
    def display(self):
        """Return ASCII representation of board."""
        from utils import display_board_ascii, piece_symbol
        
        # Convert grid to display symbols
        display_grid = []
        for row in self.grid:
            display_row = []
            for cell in row:
                if cell == '.':
                    display_row.append('.')
                else:
                    # Option 1: Standard algebraic notation (r/n/b/q/k/p for black, R/N/B/Q/K/P for white)
                    # if cell.color == 'black':
                    #     display_row.append(cell.type.lower())  # r, n, b, q, k, p
                    # else:
                    #     display_row.append(cell.type.upper())  # R, N, B, Q, K, P
                    
                    # Option 2: Unicode chess symbols (uncomment below to use instead)
                    display_row.append(piece_symbol(cell.type, cell.color))
            display_grid.append(display_row)
        
        return display_board_ascii(display_grid)
    
    def to_fen(self):
        """Export board state to FEN string."""
        from state_manager import board_to_fen
        return board_to_fen(self)
    
    @classmethod
    def from_fen(cls, fen_string):
        """Import board state from FEN string."""
        from state_manager import fen_to_board
        return fen_to_board(fen_string)