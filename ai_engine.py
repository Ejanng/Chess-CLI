import math
from validator import MoveValidator
from board import Board

class ChessAI:
    """
    Chess AI using Minimax with Alpha-Beta Pruning.
    Models game tree as NFA state exploration with heuristic evaluation.
    """
    
    # Piece values for evaluation
    PIECE_VALUES = {
        'P': 100, 'N': 320, 'B': 330,
        'R': 500, 'Q': 900, 'K': 20000
    }
    
    # Positional bonuses (simplified)
    POSITION_TABLES = {
        'P': [  # Pawn positional values
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ],
        'N': [  # Knight positional values
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]
    }
    
    def __init__(self, color, depth=3):
        self.color = color      # 'white' or 'black'
        self.depth = depth      # Search depth (NFA exploration depth)
        self.nodes_evaluated = 0
    
    def get_best_move(self, board):
        """
        Find best move using minimax with α-β pruning.
        Returns: ((from_r, from_c), (to_r, to_c), promotion_choice)
        """
        self.nodes_evaluated = 0
        validator = MoveValidator(board)
        
        legal_moves = validator.get_all_legal_moves(self.color)
        
        if not legal_moves:
            return None
        
        best_move = None
        best_value = -math.inf if self.color == 'white' else math.inf
        alpha = -math.inf
        beta = math.inf
        
        for move in legal_moves:
            from_coords, to_coords = move
            
            # Simulate move
            new_board = self._simulate_move(board, from_coords, to_coords)
            
            # Evaluate
            value = self._minimax(
                new_board, 
                self.depth - 1, 
                alpha, beta, 
                self.color != 'white'  # Next turn is opponent
            )
            
            if self.color == 'white':
                if value > best_value:
                    best_value = value
                    best_move = move
                alpha = max(alpha, value)
            else:
                if value < best_value:
                    best_value = value
                    best_move = move
                beta = min(beta, value)
        
        from_coords, to_coords = best_move
        
        # Check for promotion
        piece = board.get_piece(from_coords[0], from_coords[1])
        promotion = None
        if piece != '.' and piece.type == 'P':
            if to_coords[0] == 0 or to_coords[0] == 7:
                promotion = 'q'  # Auto-promote to queen
        
        return (from_coords, to_coords, promotion)
    
    def _minimax(self, board, depth, alpha, beta, is_maximizing):
        """
        Minimax algorithm with α-β pruning.
        NFA state exploration with pruning to reduce branching.
        """
        self.nodes_evaluated += 1
        validator = MoveValidator(board)
        
        # Terminal conditions
        current_color = 'white' if is_maximizing else 'black'
        
        # Check game end
        has_moves = validator.has_any_legal_moves(current_color)
        is_check = validator.is_in_check(current_color)
        
        if not has_moves:
            if is_check:
                # Checkmate - worst for current player
                return -100000 if is_maximizing else 100000
            else:
                # Stalemate
                return 0
        
        if depth == 0:
            return self._evaluate_board(board)
        
        legal_moves = validator.get_all_legal_moves(current_color)
        
        if is_maximizing:
            max_eval = -math.inf
            for move in legal_moves:
                from_coords, to_coords = move
                new_board = self._simulate_move(board, from_coords, to_coords)
                eval_score = self._minimax(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # β cutoff (prune NFA branch)
            return max_eval
        else:
            min_eval = math.inf
            for move in legal_moves:
                from_coords, to_coords = move
                new_board = self._simulate_move(board, from_coords, to_coords)
                eval_score = self._minimax(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # α cutoff (prune NFA branch)
            return min_eval
    
    def _simulate_move(self, board, from_coords, to_coords):
        """Create board copy with move applied."""
        new_board = board.copy()
        from_r, from_c = from_coords
        to_r, to_c = to_coords
        
        piece = new_board.get_piece(from_r, from_c)
        new_board.set_piece(to_r, to_c, piece)
        new_board.set_piece(from_r, from_c, '.')
        piece.has_moved = True
        
        # Handle promotion (auto-queen for simplicity)
        if piece.type == 'P' and (to_r == 0 or to_r == 7):
            from pieces import Queen
            new_board.set_piece(to_r, to_c, Queen(piece.color))
        
        new_board.turn = 'black' if new_board.turn == 'white' else 'white'
        return new_board
    
    def _evaluate_board(self, board):
        """
        Evaluate board position.
        Positive = good for white, Negative = good for black.
        """
        score = 0
        
        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r, c)
                if piece == '.':
                    continue
                
                value = self.PIECE_VALUES.get(piece.type, 0)
                
                # Positional bonus
                pos_bonus = 0
                if piece.type in self.POSITION_TABLES:
                    # Flip table for black pieces
                    table = self.POSITION_TABLES[piece.type]
                    if piece.color == 'white':
                        pos_bonus = table[r][c]
                    else:
                        pos_bonus = table[7-r][c]  # Mirror for black
                
                piece_score = value + pos_bonus
                
                if piece.color == 'white':
                    score += piece_score
                else:
                    score -= piece_score
        
        return score
    
    def get_stats(self):
        """Return search statistics."""
        return f"Nodes evaluated: {self.nodes_evaluated}"