class Piece:
    """Base class for all chess pieces."""
    
    def __init__(self, color, piece_type):
        self.color = color          # 'white' or 'black'
        self.type = piece_type      # 'K', 'Q', 'R', 'B', 'N', 'P'
        self.has_moved = False      # For castling, pawn double-step
    
    def __repr__(self):
        return f"{self.color[0].upper()}{self.type}"
    
    def get_possible_moves(self, row, col, board):
        """
        DFA TRANSITION FUNCTION δ(state, symbol)
        Returns list of (to_row, to_col) representing all possible next states.
        Does NOT check for check/checkmate - that's handled by validator.
        """
        raise NotImplementedError
    
    def _is_valid_square(self, r, c):
        """Check if coordinates are within board bounds."""
        return 0 <= r <= 7 and 0 <= c <= 7

    def _get_grid(self, board):
        """Accept either a Board instance or a raw 8x8 grid."""
        return board.grid if hasattr(board, 'grid') else board

    def _get_piece(self, board, r, c):
        """Return the piece on a square, or None if out of bounds."""
        if not self._is_valid_square(r, c):
            return None
        return self._get_grid(board)[r][c]
    
    def _can_capture(self, board, r, c):
        """Check if square has enemy piece."""
        piece = self._get_piece(board, r, c)
        if piece is None:
            return False
        if piece == '.':
            return False
        return piece.color != self.color
    
    def _is_empty(self, board, r, c):
        """Check if square is empty."""
        piece = self._get_piece(board, r, c)
        return piece == '.'


class Pawn(Piece):
    """Pawn piece with DFA transition rules."""
    
    def __init__(self, color):
        super().__init__(color, 'P')
        self.direction = -1 if color == 'white' else 1  # White moves up (decreasing row)
    
    def get_possible_moves(self, row, col, board):
        moves = []
        d = self.direction
        
        # Single step forward (DFA: δ(state, 'forward1') -> new_state)
        new_r = row + d
        if self._is_empty(board, new_r, col):
            moves.append((new_r, col))
            
            # Double step from starting position
            start_row = 6 if self.color == 'white' else 1
            if row == start_row:
                new_r2 = row + 2 * d
                if self._is_empty(board, new_r2, col):
                    moves.append((new_r2, col))
        
        # Captures (DFA: δ(state, 'capture_left') -> new_state)
        for dc in [-1, 1]:
            cap_r = row + d
            cap_c = col + dc
            if self._can_capture(board, cap_r, cap_c):
                moves.append((cap_r, cap_c))
        
        # En passant uses board metadata in addition to board geometry.
        en_passant_target = getattr(board, 'en_passant_target', None)
        if en_passant_target:
            ep_r, ep_c = en_passant_target
            if ep_r == row + d and abs(ep_c - col) == 1 and self._is_empty(board, ep_r, ep_c):
                adjacent_piece = self._get_piece(board, row, ep_c)
                if (adjacent_piece not in (None, '.') and adjacent_piece.type == 'P'
                        and adjacent_piece.color != self.color):
                    moves.append((ep_r, ep_c))
        
        return moves


class Knight(Piece):
    """Knight piece with L-shaped DFA transitions."""
    
    def __init__(self, color):
        super().__init__(color, 'N')
    
    def get_possible_moves(self, row, col, board):
        moves = []
        # L-shape offsets: 8 possible transitions from any state
        offsets = [(-2,-1), (-2,1), (-1,-2), (-1,2),
                   (1,-2), (1,2), (2,-1), (2,1)]
        
        for dr, dc in offsets:
            new_r, new_c = row + dr, col + dc
            if self._is_valid_square(new_r, new_c):
                if self._is_empty(board, new_r, new_c) or self._can_capture(board, new_r, new_c):
                    moves.append((new_r, new_c))
        
        return moves


class Bishop(Piece):
    """Bishop with diagonal DFA transitions (sliding piece)."""
    
    def __init__(self, color):
        super().__init__(color, 'B')
    
    def get_possible_moves(self, row, col, board):
        moves = []
        directions = [(-1,-1), (-1,1), (1,-1), (1,1)]  # 4 diagonal directions
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while self._is_valid_square(r, c):
                if self._is_empty(board, r, c):
                    moves.append((r, c))
                elif self._can_capture(board, r, c):
                    moves.append((r, c))
                    break  # Blocked by enemy piece
                else:
                    break  # Blocked by own piece
                r += dr
                c += dc
        
        return moves


class Rook(Piece):
    """Rook with orthogonal DFA transitions (sliding piece)."""
    
    def __init__(self, color):
        super().__init__(color, 'R')
    
    def get_possible_moves(self, row, col, board):
        moves = []
        directions = [(-1,0), (1,0), (0,-1), (0,1)]  # 4 orthogonal directions
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while self._is_valid_square(r, c):
                if self._is_empty(board, r, c):
                    moves.append((r, c))
                elif self._can_capture(board, r, c):
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        
        return moves


class Queen(Piece):
    """Queen combines Rook + Bishop DFA transitions."""
    
    def __init__(self, color):
        super().__init__(color, 'Q')
    
    def get_possible_moves(self, row, col, board):
        # Queen = Rook + Bishop combined
        rook_moves = Rook(self.color).get_possible_moves(row, col, board)
        bishop_moves = Bishop(self.color).get_possible_moves(row, col, board)
        return rook_moves + bishop_moves


class King(Piece):
    """King with single-step DFA transitions."""
    
    def __init__(self, color):
        super().__init__(color, 'K')
    
    def get_possible_moves(self, row, col, board):
        moves = []
        directions = [(-1,-1), (-1,0), (-1,1),
                      (0,-1),          (0,1),
                      (1,-1),  (1,0),  (1,1)]
        
        for dr, dc in directions:
            new_r, new_c = row + dr, col + dc
            if self._is_valid_square(new_r, new_c):
                if self._is_empty(board, new_r, new_c) or self._can_capture(board, new_r, new_c):
                    moves.append((new_r, new_c))
        
        castling_rights = getattr(board, 'castling_rights', None)
        if castling_rights and not self.has_moved:
            home_row = 7 if self.color == 'white' else 0
            if row == home_row and col == 4:
                kingside = f"{self.color}_kingside"
                queenside = f"{self.color}_queenside"

                if (castling_rights.get(kingside)
                        and self._castle_path_is_clear(board, row, 7, [5, 6])):
                    moves.append((row, 6))

                if (castling_rights.get(queenside)
                        and self._castle_path_is_clear(board, row, 0, [1, 2, 3])):
                    moves.append((row, 2))
        
        return moves

    def _castle_path_is_clear(self, board, row, rook_col, empty_cols):
        """Check the board geometry required for castling."""
        rook = self._get_piece(board, row, rook_col)
        if rook in (None, '.') or rook.type != 'R' or rook.color != self.color:
            return False
        return all(self._is_empty(board, row, c) for c in empty_cols)
