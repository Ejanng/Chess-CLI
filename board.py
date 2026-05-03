from pieces import Pawn, Knight, Bishop, Rook, Queen, King

class Board:
    def __init__(self):
        self.grid = [['.' for _ in range(8)] for _ in range(8)]
        self.turn = 'white'
        self.castling_rights = {
            'white_kingside': True,
            'white_queenside': True,
            'black_kingside': True,
            'black_queenside': True
        }
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.move_history = []

    def setup_default(self):
        black_row_back = [Rook('black'), Knight('black'), Bishop('black'), Queen('black'), 
                          King('black'), Bishop('black'), Knight('black'), Rook('black')]
        for c, piece in enumerate(black_row_back):
            self.grid[0][c] = piece

        for c in range(8):
            self.grid[1][c] = Pawn('black')

        for c in range(8):
            self.grid[6][c] = Pawn('white')

        white_row_back = [Rook('white'), Knight('white'), Bishop('white'), Queen('white'),
                          King('white'), Bishop('white'), Knight('white'), Rook('white')]
        
        for c, piece in enumerate(white_row_back):
            self.grid[7][c] = piece
    
    def get_piece(self, row, col):
        if 0 <= row <= 7 and 0 <= col <= 7:
            return self.grid[row][col]
        return None
    
    def set_piece(self, row, col, piece):
        self.grid[row][col] = piece

    def find_king(self, color):
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece != '.' and piece.type == 'K' and piece.color == color:
                    return (r, c)
        return None
    
    def copy(self):
        new_board = Board()
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece != '.':
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
        from state_manager import board_to_fen
        return board_to_fen(self)
    
    @classmethod
    def from_fen(cls, fen_string):
        from state_manager import fen_to_board
        return fen_to_board(fen_string)