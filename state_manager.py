from pieces import Pawn, Knight, Bishop, Rook, Queen, King

def board_to_fen(board):
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
    piece_placement = '/'.join(rows)
    active_color = 'w' if board.turn == 'white' else 'b'
    castling = ""
    if board.castling_rights['white_kingside']: castling += 'K'
    if board.castling_rights['white_queenside']: castling += 'Q'
    if board.castling_rights['black_kingside']: castling += 'k'
    if board.castling_rights['black_queenside']: castling += 'q'
    if not castling: castling = '-'
    en_passant = '-'
    if board.en_passant_target:
        from utils import coords_to_squares
        ep = coords_to_squares(*board.en_passant_target)
    
    fen = f"{piece_placement} {active_color} {castling} {ep} {board.halfmove_clock} {board.fullmove_number}"
    return fen

def fen_to_board(fen_string):
    from board import Board
    parts = fen_string.strip().split()
    if len(parts) < 4:
        raise ValueError("Invalid FEN string")
    
    board = Board()
    rows = parts[0].split('/')
    piece_map = {
        'P': Pawn, 'N': Knight, 'B': Bishop, 'R': Rook, 'Q': Queen, 'K': King,
    }
    for r, row in enumerate(rows):
        c = 0
        for char in row:
            if char.isdigit():
                for _ in range(int(char)):
                    board.set_piece(r, c, '.')
                    c += 1
            else:
                color = 'white' if char.isupper() else 'black'
                ptype = char.upper()
                board.grid[r][c] = piece_map[ptype](color)
                c += 1

    board.turn = 'white' if parts[1] == 'w' else 'black'
    castling = parts[2]
    board.castling_rights = {
        'white_kingside': 'K' in castling,
        'white_queenside': 'Q' in castling,
        'black_kingside': 'k' in castling,
        'black_queenside': 'q' in castling,
    }
    if parts[3] != '-':
        from utils import square_to_coords
        board.en_passant_target = square_to_coords(parts[3])
    else:
        board.en_passant_target = None

    if len(parts) > 4:
        board.halfmove_clock = int(parts[4])
    if len(parts) > 5:
        board.fullmove_number = int(parts[5])
    return board

def save_game_to_file(board, filename):
    fen = board_to_fen(board)
    with open(filename, 'w') as f:
        f.write(fen + '\n')
    return True

def load_game_from_file(filename):
    with open(filename, 'r') as f:
        fen_string = f.read().strip()
    return fen_to_board(fen_string)