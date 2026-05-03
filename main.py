import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_engine import GameEngine
from ai_engine import ChessAI
from utils import parse_move, format_move, coords_to_square
from state_manager import save_game_to_file, load_game_from_file

def print_banner():
    """Display game banner."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║           AUTOMATON CHESS ENGINE v1.0                   ║
    ║     Deterministic & Non-deterministic Finite Automata     ║
    ║                    CLI Edition                            ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

def print_help():
    """Display help menu."""
    print("""
    Commands:
    ---------
    e2e4      - Make a move (e.g., pawn from e2 to e4)
    e2-e4     - Alternative move format
    save      - Save current game to file
    load      - Load game from file
    undo      - Undo last move
    fen       - Display current FEN string
    board     - Redisplay the board
    help      - Show this help menu
    quit      - Exit the game
    
    Special Moves:
    --------------
    Castling: Move king two squares (e.g., e1g1 for kingside)
    Promotion: Auto-promotes to Queen (enter move normally)
    
    Game Modes:
    -----------
    1. Human (White) vs AI (Black)
    2. Human vs Human
    """)

def get_promotion_choice():
    """Ask user for promotion piece."""
    print("\nPawn promotion! Choose piece:")
    print("  q = Queen (default)")
    print("  r = Rook")
    print("  b = Bishop")
    print("  n = Knight")
    choice = input("Choice [q]: ").strip().lower()
    if choice not in ['q', 'r', 'b', 'n']:
        choice = 'q'
    return choice

def main():
    """Main game loop."""
    print_banner()
    print_help()
    
    # Game setup
    engine = GameEngine()
    engine.new_game()
    
    # Choose game mode
    print("\nSelect game mode:")
    print("  1. Human (White) vs AI (Black)")
    print("  2. Human vs Human")
    mode = input("Enter choice [1]: ").strip()
    
    ai = None
    if mode != '2':
        depth = input("AI difficulty (1-5, default 3): ").strip()
        try:
            depth = int(depth)
            if depth < 1 or depth > 5:
                depth = 3
        except:
            depth = 3
        ai = ChessAI('black', depth=depth)
        print(f"AI opponent ready (depth={depth})")
    
    print("\n" + "=" * 50)
    print(engine.board.display())
    print(engine.get_status_message())
    
    while engine.state == 'playing':
        current_player = engine.board.turn
        
        # AI turn
        if ai and current_player == ai.color:
            print(f"\n[AI thinking...]")
            result = ai.get_best_move(engine.board)
            if result:
                from_coords, to_coords, promotion = result
                success, msg = engine.make_move(from_coords, to_coords, promotion)
                if success:
                    move_str = format_move(from_coords, to_coords)
                    print(f"AI plays: {move_str}")
                    print(ai.get_stats())
                else:
                    print(f"AI error: {msg}")
            else:
                print("AI has no moves!")
            print("\n" + engine.board.display())
            print(engine.get_status_message())
            continue
        
        # Human turn
        prompt = f"\n{current_player.capitalize()}> "
        user_input = input(prompt).strip().lower()
        
        if not user_input:
            continue
        
        # Commands
        if user_input == 'quit' or user_input == 'q':
            print("Thanks for playing!")
            sys.exit(0)
        
        elif user_input == 'help' or user_input == 'h':
            print_help()
            continue
        
        elif user_input == 'board' or user_input == 'b':
            print(engine.board.display())
            print(engine.get_status_message())
            continue
        
        elif user_input == 'fen' or user_input == 'f':
            print("FEN:", engine.board.to_fen())
            continue
        
        elif user_input == 'undo' or user_input == 'u':
            success, msg = engine.undo_move()
            print(msg)
            if success:
                # If AI was opponent, undo twice to get back to human turn
                if ai and engine.board.turn == ai.color:
                    success2, msg2 = engine.undo_move()
                    if success2:
                        print("Also undone AI move.")
                print(engine.board.display())
                print(engine.get_status_message())
            continue
        
        elif user_input == 'save' or user_input == 's':
            filename = input("Save filename [chess_save.fen]: ").strip()
            if not filename:
                filename = "chess_save.fen"
            try:
                save_game_to_file(engine.board, filename)
                print(f"Game saved to {filename}")
            except Exception as e:
                print(f"Save failed: {e}")
            continue
        
        elif user_input == 'load' or user_input == 'l':
            filename = input("Load filename [chess_save.fen]: ").strip()
            if not filename:
                filename = "chess_save.fen"
            try:
                new_board = load_game_from_file(filename)
                # Update engine with loaded board
                engine.board = new_board
                engine.validator = __import__('validator').MoveValidator(new_board)
                engine.state = 'playing'
                engine.move_log = []
                print(f"Game loaded from {filename}")
                print(engine.board.display())
                print(engine.get_status_message())
            except Exception as e:
                print(f"Load failed: {e}")
            continue
        
        # Parse move
        move = parse_move(user_input)
        if not move:
            print("Invalid move format. Use 'e2e4' or 'e2-e4'.")
            continue
        
        from_coords, to_coords = move
        
        # Check for promotion
        piece = engine.board.get_piece(from_coords[0], from_coords[1])
        promotion = None
        if piece != '.' and piece.type == 'P':
            to_r = to_coords[0]
            if to_r == 0 or to_r == 7:
                promotion = get_promotion_choice()
        
        # Make move
        success, msg = engine.make_move(from_coords, to_coords, promotion)
        if not success:
            print(f"Invalid move: {msg}")
            continue
        
        move_str = format_move(from_coords, to_coords)
        print(f"Move: {move_str}")
        print(engine.board.display())
        print(engine.get_status_message())
    
    # Game over
    print("\n" + "=" * 50)
    print("GAME OVER")
    print(engine.get_status_message())
    print("Final board:")
    print(engine.board.display())
    print("FEN:", engine.board.to_fen())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
        sys.exit(0)