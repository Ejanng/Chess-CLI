class Piece:
    def __init__(self, color, piece_type):
        self.color = color
        self.type = piece_type
        self.has_moved = False

    def __repr__(self):
        return f"{self.color[0].upper()}{self.type}"
    
    def get_possible_moves(self, row, col, board):
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def _is_valid_square(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8
    
    def _can_capture(self, board, row, col):
        if not self._is_valid_square(row, col):
            return False
        piece = board[row][col]
        if piece == '.':
            return False
        return piece.color != self.color
    
    def _is_empty(self, board, row, col):
        if not self._is_valid_square(row, col):
            return False
        return board[row][col] == '.'
    
class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color, 'P')
        self.direction = -1 if color == 'white' else 1

    def get_possible_moves(self, row, col, board):
        moves = []
        d = self.direction

        new_r = row + d
        if self._is_empty(board, new_r, col):
            moves.append((new_r, col))

            start_row = 6 if self.color == 'white' else 1
            if row == start_row:
                new_r2 = row + 2 * d
                if self._is_empty(board, new_r2, col):
                    moves.append((new_r2, col))

        for dc in [-1, 1]:
            cap_r = row + d
            cap_c = col + dc
            if self._can_capture(board, cap_r, cap_c):
                moves.append((cap_r, cap_c))
        return moves
class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, 'N')

    def get_possible_moves(self, row, col, board):
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in offsets:
            new_r, new_c = row + dr, col + dc
            if self._is_valid_square(new_r, new_c):
                if self._is_empty(board, new_r, new_c) or self._can_capture(board, new_r, new_c):
                    moves.append((new_r, new_c))
        return moves
    
class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, 'B')

    def get_possible_moves(self, row, col, board):
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            new_r, new_c = row + dr, col + dc
            while self._is_valid_square(new_r, new_c):
                if self._is_empty(board, new_r, new_c):
                    moves.append((new_r, new_c))
                elif self._can_capture(board, new_r, new_c):
                    moves.append((new_r, new_c))
                    break
                else:
                    break
                new_r += dr
                new_c += dc
        return moves

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color, 'R')

    def get_possible_moves(self, row, col, board):
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            new_r, new_c = row + dr, col + dc
            while self._is_valid_square(new_r, new_c):
                if self._is_empty(board, new_r, new_c):
                    moves.append((new_r, new_c))
                elif self._can_capture(board, new_r, new_c):
                    moves.append((new_r, new_c))
                    break
                else:
                    break
                new_r += dr
                new_c += dc
        return moves

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color, 'Q')

    def get_possible_moves(self, row, col, board):
        rook_moves = Rook(self.color).get_possible_moves(row, col, board)
        bishop_moves = Bishop(self.color).get_possible_moves(row, col, board)
        return rook_moves + bishop_moves
    
class King(Piece):
    def __init__(self, color):
        super().__init__(color, 'K')

    def get_possible_moves(self, row, col, board):
        moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            new_r, new_c = row + dr, col + dc
            if self._is_valid_square(new_r, new_c):
                if self._is_empty(board, new_r, new_c) or self._can_capture(board, new_r, new_c):
                    moves.append((new_r, new_c))
        return moves