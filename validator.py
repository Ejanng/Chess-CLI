from board import Board

class MoveValidator:
    def __init__(self, board):
        self.board = board

    def is_valid_move(self, from_coords, to_coords):
        from_r, from_c = from_coords
        to_r, to_c = to_coords

        if not (0 <= from_r <= 7 and 0 <= from_c <= 7 and 0 <= to_r <= 7 and 0 <= to_c <= 7):
            return False
        
        piece = self.board.get_piece(from_r, from_c)

        if piece =='.':
            return False
        if piece.color != self.board.turn:
            return False
        
        possible_moves = piece.get_possible_moves(from_r, from_c, self.board.grid)

        if (to_r, to_c) not in possible_moves:
            return False
        if not self._validate_special_moves(from_coords, to_coords, piece):
            return False
        
        return True
    
    def _validate_special_moves(self, from_coords, to_coords, piece):
        from_r, from_c = from_coords
        to_r, to_c = to_coords

        if piece.type == 'K' and abs(to_c - from_c) == 2:
            return self._validate_castling(from_coords, to_coords, piece.color)
        if piece.type == 'P' and to_coords == self.board.en_passant_target:
            return True
        if piece.type == 'P' and (to_r == 0 or to_r == 7):
            return True
        return True
    
    def _validate_castling(self, king_from, king_to, color):
        from_r, from_c = king_from
        to_r, to_c = king_to

        if to_c > from_c:
            rights_key = f'{color}_kingside'
            rook_from_c = 7
            rook_to_c = 5
        else:
            rights_key = f'{color}_queenside'
            rook_from_c = 0
            rook_to_c = 3

        if not self.board.castling_rights(rights_key, False):
            return False
        
        king = self.board.get_piece(from_r, from_c)
        rook = self.board.get_piece(from_r, rook_from_c)

        if king == '.' or rook == '.' or king.has_moved or rook.has_moved:
            return False
        
        step = 1 if to_c > from_c else -1
        for c in range(from_c + step, rook_from_c, step):
            if self.board.get_piece(from_r, c) != '.':
                return False
            
        if self._is_square_attacked(from_r, from_c, color):
            return False
        
        for c in range(from_c + step, to_c + step, step):
            if self._is_square_attacked(from_r, c, color):
                return False
        return True
    
    def _is_square_attacked(self, row, col, defending_color):
        enemy_color = 'black' if defending_color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece(r, c)
                if piece != '.' and piece.color == enemy_color:
                    moves = piece.get_possible_moves(r, c, self.board.grid)
                    if (row, col) in moves:
                        if piece.type == 'P':
                            d = -1 if piece.color == 'white' else 1
                            if (row, col) in [(r + d, c - 1), (r + d, c + 1)]:
                                return True
                        else:
                            return True
        return False
    
    def _would_leave_king_in_check(self, from_coords, to_coords, piece):
        temp_board = self.board.copy()
        from_r, from_c = from_coords
        to_r, to_c = to_coords
        temp_board.set_piece(to_r, to_c)
        temp_board.set_piece(from_r, from_c, '.')
        if piece.type == 'P' and (to_r, to_c) == self.board.en_passant_target:
            cap_r = from_r
            temp_board.set_piece(cap_r, to_c, '.')
        if piece.type == 'K' and abs(to_c - from_c) == 2:
            if to_c > from_c:
                rook = temp_board.get_piece(from_r, 7)
                temp_board.set_piece(from_r, 5, rook)
                temp_board.set_piece(from_r, 7, '.')
            else:
                rook = temp_board.get_piece(from_r, 0)
                temp_board.set_piece(from_r, 3, rook)
                temp_board.set_piece(from_r, 0, '.')

        king_pos = temp_board.find_king(piece.color)
        if king_pos is None:
            return True
        
        return self._is_king_in_check(temp_board, king_pos, piece.color)

    def _is_king_in_check_on_board(self, board, king_pos, color):
        king_r, king_c = king_pos
        enemy_color = 'black' if color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r, c)
                if piece != '.' and piece.color == enemy_color:
                    moves = piece.get_possible_moves(r, c, board.grid)
                    if (king_r, king_c) in moves:
                        if piece.type == 'P':
                            d = -1 if piece.color == 'white' else 1
                            if (king_r, king_c) in [(r + d, c - 1), (r + d, c + 1)]:
                                return True
                        else:
                            return True    
        return False
    
    def is_in_check(self, color):
        king_pos = self.board.find_king(color)
        if king_pos is None:
            return False
        return self._is_king_in_check_on_board(self.board, king_pos, color)
    
    def has_any_legal_moves(self, color):
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece(r, c)
                if piece != '.' and piece.color == color:
                    moves = piece.get_possible_moves(r, c, self.board.grid)
                    for move in moves:
                        if self.is_valid_move((r, c), move):
                            return True
        return False
    
    def get_all_legal_moves(self, color):
        legal_moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece(r, c)
                if piece != '.' and piece.color == color:
                    moves = piece.get_possible_moves(r, c, self.board.grid)
                    for move in moves:
                        if self.is_valid_move((r, c), move):
                            legal_moves.append(((r, c), move))
        return legal_moves