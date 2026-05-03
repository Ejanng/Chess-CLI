from board import Board

class MoveValidator:
    """
    DFA Validator: Checks if a move is legal given current board state.
    The 'accept' condition: move is legal and doesn't leave king in check.
    The 'reject' condition: move is illegal or leaves king in check.
    """
    
    def __init__(self, board):
        self.board = board
    
    def is_valid_move(self, from_coords, to_coords):
        """
        DFA transition function δ(state, move):
        - Input: current board state + move (from, to)
        - Output: True (accept) or False (reject)
        """
        from_r, from_c = from_coords
        to_r, to_c = to_coords
        
        # Basic bounds check
        if not (0 <= from_r <= 7 and 0 <= from_c <= 7 and 
                0 <= to_r <= 7 and 0 <= to_c <= 7):
            return False
        
        piece = self.board.get_piece(from_r, from_c)
        
        # Must be a piece
        if piece == '.':
            return False
        
        # Must be current player's turn
        if piece.color != self.board.turn:
            return False
        
        # Get all pseudo-legal moves from piece's DFA transition function
        possible_moves = piece.get_possible_moves(from_r, from_c, self.board.grid)
        
        if (to_r, to_c) not in possible_moves:
            return False
        
        # Special move validation (castling, en passant, promotion)
        if not self._validate_special_moves(from_coords, to_coords, piece):
            return False
        
        # CRITICAL DFA CHECK: Move must not leave own king in check
        # This is the "accepting state" condition
        if self._would_leave_king_in_check(from_coords, to_coords, piece):
            return False
        
        return True
    
    def _validate_special_moves(self, from_coords, to_coords, piece):
        """Validate special chess moves."""
        from_r, from_c = from_coords
        to_r, to_c = to_coords
        
        # Castling validation
        if piece.type == 'K' and abs(to_c - from_c) == 2:
            return self._validate_castling(from_coords, to_coords, piece.color)
        
        # En passant validation
        if piece.type == 'P' and to_coords == self.board.en_passant_target:
            return True  # Already validated by piece generator
        
        # Pawn promotion (will be handled in game_engine)
        if piece.type == 'P' and (to_r == 0 or to_r == 7):
            return True  # Valid, promotion choice made separately
        
        return True
    
    def _validate_castling(self, king_from, king_to, color):
        """Validate castling rights and path safety."""
        from_r, from_c = king_from
        to_r, to_c = king_to
        
        # Determine which side
        if to_c > from_c:  # Kingside
            rights_key = f"{color}_kingside"
            rook_from_c = 7
            rook_to_c = 5
        else:  # Queenside
            rights_key = f"{color}_queenside"
            rook_from_c = 0
            rook_to_c = 3
        
        # Check rights
        if not self.board.castling_rights.get(rights_key, False):
            return False
        
        # King and rook must not have moved
        king = self.board.get_piece(from_r, from_c)
        rook = self.board.get_piece(from_r, rook_from_c)
        
        if king == '.' or rook == '.' or king.has_moved or rook.has_moved:
            return False
        
        # Path between king and rook must be clear
        step = 1 if to_c > from_c else -1
        for c in range(from_c + step, rook_from_c, step):
            if self.board.get_piece(from_r, c) != '.':
                return False
        
        # King cannot be in check
        if self._is_square_attacked(from_r, from_c, color):
            return False
        
        # King cannot pass through check
        for c in range(from_c + step, to_c + step, step):
            if self._is_square_attacked(from_r, c, color):
                return False
        
        return True
    
    def _is_square_attacked(self, row, col, defending_color):
        """
        Check if square is attacked by any enemy piece.
        Used for check detection and castling validation.
        """
        enemy_color = 'black' if defending_color == 'white' else 'white'
        
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece(r, c)
                if piece != '.' and piece.color == enemy_color:
                    # Get pseudo-legal moves (excluding check constraints to avoid recursion)
                    moves = piece.get_possible_moves(r, c, self.board.grid)
                    if (row, col) in moves:
                        # For pawns, need to verify it's actually an attack (not forward move)
                        if piece.type == 'P':
                            # Pawns attack diagonally only
                            d = -1 if piece.color == 'white' else 1
                            if (row, col) in [(r + d, c - 1), (r + d, c + 1)]:
                                return True
                        else:
                            return True
        return False
    
    def _would_leave_king_in_check(self, from_coords, to_coords, piece):
        """
        Simulate move and check if own king is in check.
        This is the core DFA accepting state verification.
        """
        # Create temporary board copy
        temp_board = self.board.copy()
        
        from_r, from_c = from_coords
        to_r, to_c = to_coords
        
        # Execute move on temp board
        temp_board.set_piece(to_r, to_c, piece)
        temp_board.set_piece(from_r, from_c, '.')
        
        # Handle en passant capture
        if piece.type == 'P' and (to_r, to_c) == self.board.en_passant_target:
            # Remove captured pawn
            cap_r = from_r  # Same row as moving pawn
            temp_board.set_piece(cap_r, to_c, '.')
        
        # Handle castling rook move
        if piece.type == 'K' and abs(to_c - from_c) == 2:
            if to_c > from_c:  # Kingside
                rook = temp_board.get_piece(from_r, 7)
                temp_board.set_piece(from_r, 5, rook)
                temp_board.set_piece(from_r, 7, '.')
            else:  # Queenside
                rook = temp_board.get_piece(from_r, 0)
                temp_board.set_piece(from_r, 3, rook)
                temp_board.set_piece(from_r, 0, '.')
        
        # Find king position
        king_pos = temp_board.find_king(piece.color)
        if king_pos is None:
            return True  # No king = invalid state
        
        # Check if king is attacked
        return self._is_king_in_check_on_board(temp_board, king_pos, piece.color)
    
    def _is_king_in_check_on_board(self, board, king_pos, color):
        """Check if king at position is in check on given board."""
        king_r, king_c = king_pos
        enemy_color = 'black' if color == 'white' else 'white'
        
        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r, c)
                if piece != '.' and piece.color == enemy_color:
                    moves = piece.get_possible_moves(r, c, board.grid)
                    if (king_r, king_c) in moves:
                        # Pawn special case
                        if piece.type == 'P':
                            d = -1 if piece.color == 'white' else 1
                            if (king_r, king_c) in [(r + d, c - 1), (r + d, c + 1)]:
                                return True
                        else:
                            return True
        return False
    
    def is_in_check(self, color):
        """Check if given color's king is currently in check."""
        king_pos = self.board.find_king(color)
        if king_pos is None:
            return False
        return self._is_king_in_check_on_board(self.board, king_pos, color)
    
    def has_any_legal_moves(self, color):
        """
        Check if player has any legal moves.
        Used for checkmate/stalemate detection.
        """
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
        """
        Get all legal moves for a player.
        Returns list of ((from_r, from_c), (to_r, to_c)).
        """
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