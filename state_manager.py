from pieces import Pawn, Knight, Bishop, Rook, Queen, King

def board_to_fen(board):
    """
    Convert board state to FEN string.
    FEN format: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
    """
    # Piece placement
    rows = []
    for r in range(8):
        empty_count = 0
        row_str = ""
        for c in range(8):
            piece = board.get_piece(r, c)
            if piece == '.':
                empty_count += 1
            else:
                if empty_count > 0:
                    row_str += str(empty_count)
                    empty_count = 0
                symbol = piece.type
                if piece.color == 'black':
                    symbol = symbol.lower()
                row_str += symbol
        if empty_count > 0:
            row_str += str(empty_count)
        rows.append(row_str)
    
    piece_placement = "/".join(rows)
    
    # Active color
    active_color = 'w' if board.turn == 'white' else 'b'
    
    # Castling rights
    castling = ""
    if board.castling_rights.get('white_kingside'): castling += 'K'
    if board.castling_rights.get('white_queenside'): castling += 'Q'
    if board.castling_rights.get('black_kingside'): castling += 'k'
    if board.castling_rights.get('black_queenside'): castling += 'q'
    if not castling: castling = '-'
    
    # En passant
    ep = '-'
    if board.en_passant_target:
        from utils import coords_to_square
        ep = coords_to_square(*board.en_passant_target)
    
    # Halfmove clock and fullmove number
    fen = f"{piece_placement} {active_color} {castling} {ep} {board.halfmove_clock} {board.fullmove_number}"
    return fen

def fen_to_board(fen_string):
    """
    Parse FEN string and create Board instance.
    """
    from board import Board
    
    parts = fen_string.strip().split()
    if len(parts) < 4:
        raise ValueError("Invalid FEN string")
    
    board = Board()
    
    # Parse piece placement
    rows = parts[0].split('/')
    piece_map = {
        'P': Pawn, 'N': Knight, 'B': Bishop,
        'R': Rook, 'Q': Queen, 'K': King
    }
    
    for r, row_str in enumerate(rows):
        c = 0
        for char in row_str:
            if char.isdigit():
                # Empty squares
                for _ in range(int(char)):
                    board.grid[r][c] = '.'
                    c += 1
            else:
                # Piece
                color = 'white' if char.isupper() else 'black'
                ptype = char.upper()
                board.grid[r][c] = piece_map[ptype](color)
                c += 1
    
    # Active color
    board.turn = 'white' if parts[1] == 'w' else 'black'
    
    # Castling rights
    castling = parts[2]
    board.castling_rights = {
        'white_kingside': 'K' in castling,
        'white_queenside': 'Q' in castling,
        'black_kingside': 'k' in castling,
        'black_queenside': 'q' in castling
    }
    
    # En passant
    if parts[3] != '-':
        from utils import square_to_coords
        board.en_passant_target = square_to_coords(parts[3])
    else:
        board.en_passant_target = None
    
    # Halfmove clock and fullmove
    if len(parts) > 4:
        board.halfmove_clock = int(parts[4])
    if len(parts) > 5:
        board.fullmove_number = int(parts[5])
    
    return board

def save_game_to_file(board, filename):
    """Save current board state to FEN file."""
    fen = board_to_fen(board)
    with open(filename, 'w') as f:
        f.write(fen + '\n')
    return True

def load_game_from_file(filename):
    """Load board state from FEN file."""
    with open(filename, 'r') as f:
        fen = f.read().strip()
    return fen_to_board(fen)