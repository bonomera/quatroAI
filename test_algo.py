import pytest
from unittest.mock import patch, MagicMock
import random
import copy
import sys
sys.path.append('.')  # Add current directory to path if needed

# Import the module to test
import algo

class TestAlgo:
    
    def test_board_into_int(self):
        # Test conversion of 'None' strings to None values
        state = {"board": [None, 'None', 'BLEP', None, 'SDFC']}
        result = algo.board_into_int(state)
        assert result == [None, None, 'BLEP', None, 'SDFC']
    
    def test_piece_generation(self):
        # Test that all 16 unique pieces are generated
        pieces = algo.piece()
        assert len(pieces) == 16
        assert 'BLEP' in pieces  # Big Light Empty Pyramid
        assert 'SDFC' in pieces  # Small Dark Full Circle
        
        # Test that all pieces follow the format: size(B/S) + color(L/D) + fill(E/F) + shape(P/C)
        for p in pieces:
            assert len(p) == 4
            assert p[0] in ['B', 'S']  # Size
            assert p[1] in ['L', 'D']  # Color
            assert p[2] in ['E', 'F']  # Fill
            assert p[3] in ['P', 'C']  # Shape
    
    def test_conversion_piece(self):
        # Test standardization of piece notation
        assert algo.conversion_piece('BLEP') == 'BLEP'  # Already standard
        assert algo.conversion_piece('BDFC') == 'BDFC'  # Already standard
        assert algo.conversion_piece(None) is None     # None stays None
        
        # Non-standard order should be standardized
        mixed_piece = 'PBEL'  # Pyramid Big Empty Light in non-standard order
        assert algo.conversion_piece(mixed_piece) == 'BLEP'  # Should reorder to standard
    
    def test_same(self):
        # Test if pieces share at least one attribute
        # Same size (B)
        assert algo.same(['BLEP', 'BDFC', 'BLFC']) == True
        
        # Different in all attributes
        assert algo.same(['BLEP', 'SDFC']) == False
        
        # Contains None
        assert algo.same(['BLEP', None, 'BDFC']) == False
        
        # Same color (D)
        assert algo.same(['BDEP', 'SDFC', 'SDEP']) == True
    
    def test_getLine(self):
        # Test retrieving a row from the board
        board = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        assert algo.getLine(board, 0) == [0, 1, 2, 3]
        assert algo.getLine(board, 2) == [8, 9, 10, 11]
    
    def test_getColumn(self):
        # Test retrieving a column from the board
        board = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        assert algo.getColumn(board, 0) == [0, 4, 8, 12]
        assert algo.getColumn(board, 3) == [3, 7, 11, 15]
    
    def test_getDiagonal(self):
        # Test retrieving diagonals from the board
        board = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        
        # Main diagonal (top-left to bottom-right)
        assert algo.getDiagonal(board, 1) == [0, 5, 10, 15]
        
        # Secondary diagonal (top-right to bottom-left)
        assert algo.getDiagonal(board, -1) == [2, 5, 8, 11]
    
    def test_winner(self):
        # Test winner detection with a win in a row
        state = {
            "current": 1,  # Current player is 1, so player 0 made the last move
            "board": ['BLEP', 'BLFC', 'BDEP', 'BDFC', 
                      None, None, None, None, 
                      None, None, None, None, 
                      None, None, None, None]
        }
        # First row has all big pieces (shared attribute B), so player 0 wins
        assert algo.winner(state) == 0
        
        # Test with no winner
        state["board"] = [None] * 16
        assert algo.winner(state) is False
    
    def test_utility(self):
        # Test utility calculation for terminal states
        player = 0
        
        # Player 0 wins
        state = {
            "current": 1,  # Last move was by player 0
            "board": ['BLEP', 'BLFC', 'BDEP', 'BDFC',  # Win in first row (all Big)
                      None, None, None, None, 
                      None, None, None, None, 
                      None, None, None, None]
        }
        assert algo.utility(state, player) == float('inf')
        
        # Player 0 loses
        state["current"] = 0  # Last move was by player 1
        assert algo.utility(state, player) == -float('inf')
        
        # Draw (full board, no winner)
        state = {
            "current": 0,
            "board": ['BLEP', 'SDFC', 'BDFC', 'SLEP',
                      'SDEP', 'BLFC', 'SLFC', 'BDEP',
                      'BLEC', 'SDEC', 'BDEC', 'SLEC',
                      'SDFP', 'BLFP', 'SLFP', 'BDFP']
        }
        # Mock the winner function to return False (no winner)
        with patch('algo.winner', return_value=False):
            assert algo.utility(state, player) == 0
    
    def test_currentPlayer(self):
        # Test current player extraction
        state = {"current": 0}
        assert algo.currentPlayer(state) == 0
        
        state = {"current": 1}
        assert algo.currentPlayer(state) == 1
    
    def test_isFull(self):
        # Test board fullness check
        # Empty board
        board = [None] * 16
        assert algo.isFull(board) == False
        
        # Partially filled board
        board = ['BLEP', None, 'BDFC', None]
        assert algo.isFull(board) == False
        
        # Full board
        board = ['BLEP', 'SDFC', 'BDFC', 'SLEP'] * 4
        assert algo.isFull(board) == True
    
    @patch('copy.deepcopy')
    def test_apply(self, mock_deepcopy):
        # Test move application
        state = {
            "current": "0",
            "board": [None] * 16,
            "piece": "BLEP"
        }
        # Setup the mock to return a copy of the state
        mock_deepcopy.return_value = copy.deepcopy(state)
        
        # Apply a valid move
        result = algo.apply(state, (5, "BLEP", "SDFC"))
        
        # Check the move was applied correctly
        assert result["board"][5] == "BLEP"
        assert result["current"] == "1"  # Player changed from 0 to 1
        assert result["piece"] == "SDFC"
    
    def test_check_threat(self):
        # Test threat detection (3 pieces with a common attribute)
        # Line with a threat (all big)
        line = ['BLEP', 'BDFC', 'BLFC', None]
        assert algo.check_threat(line) == True
        
        # Line without a threat
        line = ['BLEP', 'SDFC', None, None]
        assert algo.check_threat(line) == False
        
        # Line with more than 3 pieces
        line = ['BLEP', 'BDFC', 'BLFC', 'BDEP']
        assert algo.check_threat(line) == False
    
    def test_evaluate_heuristic(self):
        # Test heuristic evaluation
        state = {
            "board": [None] * 16
        }
        player = 0
        
        # Empty board should have a baseline score
        score_empty = algo.evaluate_heuristic(state, player)
        
        # Add pieces to create threats and center control
        state["board"][0] = 'BLEP'
        state["board"][1] = 'BDFC'
        state["board"][2] = 'BLFC'  # Creates a threat in first row (all big)
        
        state["board"][5] = 'SDFC'  # Center piece (index 5 is one of the center positions)
        
        score_with_threat_and_center = algo.evaluate_heuristic(state, player)
        
        # Score should increase with threats and center control
        assert score_with_threat_and_center > score_empty
    
    @patch('algo.evaluate_heuristic')
    @patch('algo.utility')
    def test_negamax(self, mock_utility, mock_evaluate):
        # Test negamax algorithm with various scenarios
        state = {
            "players": ["Player1", "Player2"],
            "current": "0",
            "board": [None] * 16, 
            "piece": "BLEP"
        }
        player = "0"
        depth = 2
        
        # Terminal state case
        with patch('algo.winner', return_value=0):
            with patch('algo.isFull', return_value=True):
                mock_utility.return_value = float('inf')
                result = algo.negamax(state, player, depth)
                assert result == float('inf')
        
        # Non-terminal state at depth 0
        with patch('algo.winner', return_value=False):
            with patch('algo.isFull', return_value=False):
                mock_evaluate.return_value = 42
                result = algo.negamax(state, player, 0)
                assert result == 42
    
    @patch('algo.negamax')
    def test_find_best_negamax_move(self, mock_negamax):
        # Test move selection
        state = {
                "players": ["LUR", "FKY"],
                "current": 0,
                "board": [
                    'BDEP', 'SDEP', None,  None,
                    'BLEP', 'BLEC', 'BLFP', None,
                    'SLEC', 'SLFP', 'SLFC', None,
                    None,   None,  None,   None
                ],
                "piece": "BLEP"}
        player = "0"
        depth = 2
        
        # Mock negamax to return higher score for position 3
        def mock_negamax_side_effect(next_state, opponent, depth, alpha, beta):
            pos = next_state["board"].index("BLEP")
            if pos == 7:
                return -100  # Higher negated score for opponent means better for current player
            return -50
        
        mock_negamax.side_effect = mock_negamax_side_effect
        
        # Find best move with mocked evaluation
        with patch('algo.piece', return_value=['SDFC', 'BDFC']):
            pos, piece = algo.find_best_negamax_move(state, player, depth)
            print(pos,piece)
            assert pos == 7
            assert piece in ['SDFC', 'BDFC']
    
    @patch('algo.find_best_negamax_move')
    def test_game(self, mock_find_best):
        # Test main game function with different board states
        mock_find_best.return_value = (3, 'SDFC')
        
        # Empty board
        state = {
            "players": ["Player1", "Player2"],
            "current": "0",
            "board": [None] * 16,
            "piece": "BLEP"
        }
        pos, piece = algo.game(state)
        assert pos == 3
        
        # Mid-game (7-9 pieces on board should increase depth)
        state["board"] = ['BLEP', 'BDFC', 'BLFC', None,
                         'SDFC', 'SLEP', 'BDEP', None,
                         None, None, None, None,
                         None, None, None, None]
        pos, piece = algo.game(state)
        assert pos == 3
        
        # Late game (10-13 pieces should set depth to 8)
        state["board"] = ['BLEP', 'BDFC', 'BLFC', None,
                         'SDFC', 'SLEP', 'BDEP', 'SLFC',
                         'BLEC', 'SDEC', None, None,
                         None, None, None, None]
        pos, piece = algo.game(state)
        assert pos == 3


if __name__ == "__main__":
    pytest.main(["-v", "test_algo.py"])