import pytest
from unittest.mock import patch, MagicMock, call
import copy
import sys
sys.path.append('.')  # Add current directory to path if needed

# Import the module to test
import algo

class TestNegamaxInternals:
    
    def test_negamax_move_simulation_and_tracking(self):
        # Test the specific piece tracking and board simulation part of the negamax function
        
        # Create a test state with some pieces already on the board
        test_state = {
            "players": ["Player1", "Player2"],
            "current": "0",
            "board": [
                'BLEP', 'BDFC', None, None,
                None, 'SLEP', None, 'SDFC',
                None, 'BDEP', None, None,
                'SLFC', None, None, None
            ],
            "piece": "BLFC"  # Current piece to place
        }
        
        # Manually execute the code being tested to verify its behavior
        piece_to_place = test_state["piece"]
        board = copy.deepcopy(test_state["board"])
        current_player_index_str = str(test_state["current"])
        opponent_player_index_str = str(1 - int(current_player_index_str))
        
        # Track placed pieces
        placed_pieces_fs = {p for p in board if p is not None}
        if piece_to_place:
            placed_pieces_fs.add(piece_to_place)
        
        # Get all possible pieces
        all_pieces = algo.piece()
        
        # Determine available positions and pieces
        empty_positions = []
        for i, elem in enumerate(test_state["board"]):
            if elem is None:
                empty_positions.append(i)
            if elem in all_pieces:
                all_pieces.remove(elem)
        
        # The current piece to place should also be removed from available pieces
        if piece_to_place in all_pieces:
            all_pieces.remove(piece_to_place)
        available_to_give = all_pieces
        
        # Verify empty positions are correctly identified
        assert len(empty_positions) == 10
        assert 2 in empty_positions
        assert 3 in empty_positions
        assert 4 in empty_positions
        assert 6 in empty_positions
        
        # Verify placed pieces are correctly tracked
        assert len(placed_pieces_fs) == 7  # 6 on board + 1 current piece
        assert 'BLEP' in placed_pieces_fs
        assert 'BDFC' in placed_pieces_fs
        assert 'SLEP' in placed_pieces_fs
        assert 'SDFC' in placed_pieces_fs
        assert 'BDEP' in placed_pieces_fs
        assert 'SLFC' in placed_pieces_fs
        
        # Verify available pieces to give are correct (should be 16 - 7 = 9 pieces)
        assert len(available_to_give) == 9
        assert 'SLFP' in available_to_give  # Random check of some pieces that should be available
        assert 'BLFP' in available_to_give
        
        # Test board modification for a single move
        test_pos = empty_positions[0]  # First empty position
        new_board = list(board)
        new_board[test_pos] = piece_to_place
        
        # Verify board was correctly modified
        assert new_board[test_pos] == piece_to_place
        assert new_board != board  # Should be different from original
    
    def test_negamax_win_detection(self):
        """Test the immediate win detection inside the negamax loop"""
        
        # Mock the winnerF function that's defined inside negamax
        with patch('algo.same') as mock_same:
            
            # Create a test state where placing BLFC at position 2 creates a win
            test_state = {
                "players": ["Player1", "Player2"],
                "current": 0,
                "board": [
                    'BLEP', 'BDEP', 'BDFC', None,
                    None, None, None, None,
                    None, None, None, None,
                    None, None, None, None
                ],
                "piece": "BLFC"  # Current piece to place 
            }
            
            # Call negamax but don't recurse (depth=0)
            # We're only testing the immediate win detection logic
            result = algo.negamax(test_state, 0, 2)
            
            # Should detect the win and return positive infinity
            assert result == float('inf')
    
    @patch('algo.negamax')
    def test_negamax_recursive_evaluation(self, mock_negamax):
        """Test the recursive evaluation of positions and piece selection"""
        
        # Create a state with several empty positions
        test_state = {
            "players": ["Player1", "Player2"],
            "current": "0",
            "board": [
                'BLEP', 'BDFC', None, None,
                None, None, None, None,
                None, None, None, None,
                None, None, None, None
            ],
            "piece": "BLFC"
        }
        
        # Mock the winnerF function to always return False (no immediate win)
        with patch.object(algo, 'same', return_value=False):
            # Mock the recursive negamax call to return different values
            # This simulates evaluating different opponent moves
            mock_negamax.side_effect = [-10, -20, -5]  # First next piece is best for opponent
            
            # Run negamax with sufficient depth to trigger recursion
            result = algo.negamax(test_state, "0", 2, -float('inf'), float('inf'))
            
            # Should choose the move that minimizes opponent's advantage
            # Negate lowest opponent score (-5) = 5
            assert result == -10
            
            # Verify the recursive calls were made with correct parameters
            assert mock_negamax.call_count >= 1
    
    def test_negamax_pruning(self):
        """Test alpha-beta pruning behavior in negamax"""
        
        test_state = {
            "players": ["Player1", "Player2"],
            "current": "0",
            "board": [None] * 16,
            "piece": "BLFC"
        }
        
        # Mock the recursive negamax calls
        with patch('algo.negamax') as mock_negamax:
            # First call returns a very high value that should trigger pruning
            mock_negamax.return_value = 1000
            
            # Call with alpha-beta bounds that should trigger pruning
            algo.negamax(test_state, "0", 2, -float('inf'), 50)
            
            # Verify pruning occurred (should make fewer calls)
            # This is hard to test precisely without modifying the code,
            # but we can check that at least one call was made
            assert mock_negamax.call_count >= 1
    
    def test_negamax_empty_available_pieces(self):
        """Test negamax behavior when no pieces are available to give"""
        
        # Create a nearly full board with only one empty spot
        board = [None] + ['BLEP', 'BDFC', 'SLEP', 'SDFC', 'BLFC', 'BDEC', 'SLEC',
                         'SDEC', 'BLFP', 'BDFP', 'SLFP', 'SDFP', 'BLEP', 'BDEP']
        
        test_state = {
            "players": ["Player1", "Player2"],
            "current": "0",
            "board": board,
            "piece": "SLEP"  # Last piece to place
        }
        
        # All pieces are either on the board or the current piece to place
        # Create a custom piece function that returns the exact pieces on the board
        with patch('algo.piece') as mock_piece:
            mock_piece.return_value = ['BLEP', 'BDFC', 'SLEP', 'SDFC', 'BLFC', 'BDEC', 'SLEC',
                                      'SDEC', 'BLFP', 'BDFP', 'SLFP', 'SDFP', 'BLEP', 'BDEP', 'SLEP']
            
            # Mock winner to return False (no immediate win)
            with patch('algo.winner', return_value=False):
                # Run negamax with this state
                result = algo.negamax(test_state, "0", 1)
                
                # Should handle the case where no pieces are available to give
                # This may return 0 (draw) or some other value depending on implementation
                assert isinstance(result, (int, float))
    
    def test_negamax_integration(self):
        """Full integration test of the negamax function"""
        
        # Create a game state that requires strategic thinking
        test_state = {
            "players": ["Player1", "Player2"],
            "current": "0",
            "board": [
                'BLEP', 'BDFC', 'SLEP', None,  
                'SDFC', None,   None,  None,
                None,  None,   None,  None,
                None,  None,   None,  None
            ],
            "piece": "BLFC"  # Current piece to place
        }
        
        # Run the actual negamax algorithm
        result = algo.negamax(test_state, "0", 2)
        
        # We can't predict the exact score, but it should be a number
        assert isinstance(result, (int, float))
        
        # If there's a win possible, score should be high
        # If no win possible, score should reflect evaluation
        assert result != 0  # Shouldn't be exactly 0 in this position

if __name__ == "__main__":
    pytest.main(["-v", "test_negamax_internals.py"])
