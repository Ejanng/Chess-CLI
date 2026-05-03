from board import Board
from validator import MoveValidator
from pieces import Pawn, Rook, Queen, Bishop, Knight

class GameEngine:
    """
    Chess Game State Machine
    States: 'playing', 'checkmate', 'stalemate', 'draw'
    Transitions: player moves trigger state changes
    """
    
    def __init__(self):
        self.board = Board()
        self.validator = MoveValidator(self.board)
        self.state = 'playing'  # DFA states: playing, checkmate, stalemate, draw
        self.winner = None
        self.move_log = []
    
    def new_game(self):
        """Initialize new game."""
        self.board.setup_default()
        self.validator = MoveValidator(self.board)
        self.state = 'playing'
        self.winner = None
        self.move_log = []
    
    def make_move(self, from_coords, to_coords, promotion_choice=None):
        """
        Execute a move and transition game state.
        Returns: (success: bool, message: str)
        """
        if self.state != 'playing':
            return False, f"Game is over. State: {self.state}"
        
        # DFA validation
        if not self.validator.is_valid_move(from_coords, to_coords):
            return False, "Illegal move."
        
        from_r, from_c = from_coords
        to_r, to_c = to_coords
        piece = self.board.get_piece(from_r, from_c)
        
        # Record move for history (PDA stack push)
        move_record = {
            'from': from_coords,
            'to': to_coords,
            'piece': piece.__repr__(),
            'captured': self.board.get_piece(to_r, to_c).__repr__() if self.board.get_piece(to_r, to_c) != '.' else None,
            'castling_rights': self.board.castling_rights.copy(),
            'en_passant': self.board.en_passant_target,
            'halfmove': self.board.halfmove_clock,
            'has_moved': piece.has_moved
        }
        
        # Execute the move
        self._execute_move(from_coords, to_coords, promotion_choice)
        
        # Update move history
        self.move_log.append(move_record)
        
        # Update en passant target
        self._update_en_passant(from_coords, to_coords, piece)
        
        # Update castling rights
        self._update_castling_rights(from_coords, to_coords, piece)
        
        # Update halfmove clock (for 50-move rule)
        if piece.type == 'P' or move_record['captured'] is not None:
            self.board.halfmove_clock = 0
        else:
            self.board.halfmove_clock += 1
        
        # Switch turn
        self.board.turn = 'black' if self.board.turn == 'white' else 'white'
        
        # Update fullmove number
        if self.board.turn == 'white':
            self.board.fullmove_number += 1
        
        # Recreate validator with new state
        self.validator = MoveValidator(self.board)
        
        # Check game end conditions
        self._check_game_end()
        
        return True, "Move successful."
    
    def _execute_move(self, from_coords, to_coords, promotion_choice):
        """Execute move on board."""
        from_r, from_c = from_coords
        to_r, to_c = to_coords
        piece = self.board.get_piece(from_r, from_c)
        
        # Handle en passant capture
        if piece.type == 'P' and (to_r, to_c) == self.board.en_passant_target:
            cap_r = from_r
            self.board.set_piece(cap_r, to_c, '.')
        
        # Move piece
        self.board.set_piece(to_r, to_c, piece)
        self.board.set_piece(from_r, from_c, '.')
        piece.has_moved = True
        
        # Handle castling rook move
        if piece.type == 'K' and abs(to_c - from_c) == 2:
            if to_c > from_c:  # Kingside
                rook = self.board.get_piece(from_r, 7)
                self.board.set_piece(from_r, 5, rook)
                self.board.set_piece(from_r, 7, '.')
                rook.has_moved = True
            else:  # Queenside
                rook = self.board.get_piece(from_r, 0)
                self.board.set_piece(from_r, 3, rook)
                self.board.set_piece(from_r, 0, '.')
                rook.has_moved = True
        
        # Handle pawn promotion
        if piece.type == 'P' and (to_r == 0 or to_r == 7):
            promoted = self._get_promotion_piece(promotion_choice, piece.color)
            self.board.set_piece(to_r, to_c, promoted)
    
    def _get_promotion_piece(self, choice, color):
        """Get promotion piece based on choice."""
        choices = {'q': Queen(color), 'r': Rook(color), 'b': Bishop(color), 'n': Knight(color)}
        return choices.get(choice, Queen(color))
    
    def _update_en_passant(self, from_coords, to_coords, piece):
        """Update en passant target square."""
        from_r, from_c = from_coords
        to_r, to_c = to_coords
        
        # Pawn double-step creates en passant target
        if piece.type == 'P' and abs(to_r - from_r) == 2:
            target_r = (from_r + to_r) // 2
            self.board.en_passant_target = (target_r, from_c)
        else:
            self.board.en_passant_target = None
    
    def _update_castling_rights(self, from_coords, to_coords, piece):
        """Update castling rights after move."""
        from_r, from_c = from_coords
        
        # King move removes all castling rights for that color
        if piece.type == 'K':
            if piece.color == 'white':
                self.board.castling_rights['white_kingside'] = False
                self.board.castling_rights['white_queenside'] = False
            else:
                self.board.castling_rights['black_kingside'] = False
                self.board.castling_rights['black_queenside'] = False
        
        # Rook move removes respective castling right
        if piece.type == 'R':
            if from_coords == (7, 0) and piece.color == 'white':
                self.board.castling_rights['white_queenside'] = False
            elif from_coords == (7, 7) and piece.color == 'white':
                self.board.castling_rights['white_kingside'] = False
            elif from_coords == (0, 0) and piece.color == 'black':
                self.board.castling_rights['black_queenside'] = False
            elif from_coords == (0, 7) and piece.color == 'black':
                self.board.castling_rights['black_kingside'] = False
        
        # Rook capture removes castling rights
        to_r, to_c = to_coords
        captured = self.board.get_piece(to_r, to_c)
        if captured != '.' and captured.type == 'R':
            if to_coords == (7, 0):
                self.board.castling_rights['white_queenside'] = False
            elif to_coords == (7, 7):
                self.board.castling_rights['white_kingside'] = False
            elif to_coords == (0, 0):
                self.board.castling_rights['black_queenside'] = False
            elif to_coords == (0, 7):
                self.board.castling_rights['black_kingside'] = False
    
    def _check_game_end(self):
        """Check for checkmate, stalemate, or draw conditions."""
        current_color = self.board.turn
        
        # Check if current player has any legal moves
        has_moves = self.validator.has_any_legal_moves(current_color)
        is_check = self.validator.is_in_check(current_color)
        
        if not has_moves:
            if is_check:
                self.state = 'checkmate'
                self.winner = 'black' if current_color == 'white' else 'white'
            else:
                self.state = 'stalemate'
                self.winner = None
        
        # 50-move rule
        if self.board.halfmove_clock >= 100:
            self.state = 'draw'
            self.winner = None
        
        # TODO: Threefold repetition (would require position history)
    
    def get_status_message(self):
        """Get current game status for display."""
        if self.state == 'playing':
            check_status = ""
            if self.validator.is_in_check(self.board.turn):
                check_status = " (CHECK!)"
            return f"{self.board.turn.capitalize()} to move{check_status}"
        elif self.state == 'checkmate':
            return f"CHECKMATE! {self.winner.capitalize()} wins!"
        elif self.state == 'stalemate':
            return "STALEMATE! Game is drawn."
        elif self.state == 'draw':
            return "DRAW! (50-move rule)"
        return "Unknown state"
    
    def undo_move(self):
        """
        Undo last move (PDA pop operation).
        Returns: (success: bool, message: str)
        """
        if not self.move_log:
            return False, "No moves to undo."
        
        last_move = self.move_log.pop()
        
        # Restore board state
        from_r, from_c = last_move['from']
        to_r, to_c = last_move['to']
        
        # Move piece back
        piece = self.board.get_piece(to_r, to_c)
        self.board.set_piece(from_r, from_c, piece)
        
        # Restore captured piece
        if last_move['captured']:
            # Need to reconstruct piece from symbol
            color = 'white' if last_move['captured'][0] == 'W' else 'black'
            ptype = last_move['captured'][1]
            captured_piece = self._create_piece(ptype, color)
            self.board.set_piece(to_r, to_c, captured_piece)
        else:
            self.board.set_piece(to_r, to_c, '.')
        
        # Restore metadata
        self.board.castling_rights = last_move['castling_rights']
        self.board.en_passant_target = last_move['en_passant']
        self.board.halfmove_clock = last_move['halfmove']
        piece.has_moved = last_move['has_moved']
        
        # Switch turn back
        self.board.turn = 'black' if self.board.turn == 'white' else 'white'
        
        # Update fullmove
        if self.board.turn == 'black':
            self.board.fullmove_number -= 1
        
        self.state = 'playing'
        self.winner = None
        self.validator = MoveValidator(self.board)
        
        return True, "Move undone."
    
    def _create_piece(self, ptype, color):
        """Create piece from type character."""
        from pieces import Pawn, Knight, Bishop, Rook, Queen, King
        pieces = {
            'P': Pawn, 'N': Knight, 'B': Bishop,
            'R': Rook, 'Q': Queen, 'K': King
        }
        return pieces[ptype](color)