import random
import copy
import time
from copy import deepcopy
def board_into_int(state):
    return [None if x == 'None' or x is None else x for x in state["board"]]

def piece():
    # Generates and returns a list of all 16 unique game piece strings
    pieces = []
    tailles = ['B', 'S']  # Big, Small
    couleurs = ['L', 'D']  # Light, Dark
    remplissages = ['E', 'F']  # Empty, Full
    formes = ['P', 'C']  # Square, Circle
    
    for taille in tailles:
        for couleur in couleurs:
            for remplissage in remplissages:
                for forme in formes:
                    piece = taille + couleur + remplissage + forme
                    pieces.append(piece)
    
    return pieces

def conversion_piece(piecen):
    # Standardizes a given piece 'piecen' into the canonical 4-character string format
    if piecen in piece(): # Checks if it's already in the standard list
        return piecen
    if piecen is None:
        return None
    else:
        piecen = list(piecen) # Converts input to a list of characters
        # The following variables will store the identified attribute characters
        for i in piecen: # Iterates through characters to identify attributes
            if i in ['B', 'S']:
                tailles = i 
            if i in ['L', 'D']:
                couleurs = i
            if i in ['E', 'F']:
                remplissages = i
            if i in ['P', 'C']:
                formes = i
        piece_final = tailles + couleurs + remplissages + formes # Reconstructs the piece string
    return piece_final

def same(L):
    # Checks if all pieces in a list L (a line) share at least one common attribute
    if None in L:
        return False
    common = frozenset(L[0])
    for elem in L[1:]:
        common = common & frozenset(elem)
    return len(common) > 0


def getLine(board, i):
    # Returns row
    return board[i * 4 : (i + 1) * 4]


def getColumn(board, j):
    # Returns column
    return [board[i] for i in range(j, 16, 4)]


# dir == 1 or -1
def getDiagonal(board, dir):
    # Returns a diagonal 
    start = 0 if dir == 1 else 2
    return [board[start + i * (4 + dir)] for i in range(4)]


def winner(state):
    # Determines if there is a winner in the given game state 'board_state'
    player = currentPlayer(state)
    board = state["board"] # Accesses the actual board list from the state
    # The winner is the player who made the *last* move
    for i in range(4):
        if same(getLine(board, i)):
            return 1 - player
        if same(getColumn(board, i)):
            return 1 - player
    if same(getDiagonal(board, 1)):
        return 1 - player
    if same(getDiagonal(board, -1)):
        return 1 - player
    return False

def utility(state, player):
	# Calculates the utility of a terminal game state
    theWinner = winner(state) # Determines the winner of the state
    if theWinner is False and isFull(state["board"]) is True: 
        return 0 # Draw.
    if theWinner == player: # `player_perspective` won
        return float('inf')
    return -float('inf') # `player_perspective` lost

def gameOver(state):
    # Checks if the game has ended (either by a win or a full board)
	if winner(state) is str:
		return True

	empty = 0
	for elem in state:
		if elem is None:
			empty += 1
	return empty == 0

def currentPlayer(state):
    return state["current"]

def isFull(board): # Checks if the game board has no empty (None) spots
    for elem in board:
        if elem is None:
            return False
    return True

def apply(state, move):
    position, piece, next_piece = move
    res = deepcopy(state)
    if not (0 <= position < 16 and res["board"][position] is None):
        raise ValueError("Position invalide ou déjà occupée")
    res["board"][position] = piece
    res["current"] = str(1 - int(res["current"]))
    res["piece"] = next_piece
    return res

def check_threat(line):
    # Checks if a given 'line' (row, col, or diag) has 3 pieces sharing a common attribute
    pieces = [p for p in line if p is not None] # Collect actual pieces in the line
    if len(pieces) == 3: # A threat requires exactly 3 pieces

        common_attributes = frozenset(pieces[0]) & frozenset(pieces[1]) & frozenset(pieces[2])
        return len(common_attributes) > 0 
    return False

def evaluate_heuristic(state, player):
    # Calculates a heuristic score for the board state (threats, center control)
    board = state["board"]
    score = 0

    threat_count = 0 # Counts lines with 3 pieces sharing an attribute
    lines = [] # List to hold all rows, columns, and diagonals
    for i in range(4):
        lines.append(getLine(board, i))
        lines.append(getColumn(board, i))
    lines.append(getDiagonal(board, 1))
    lines.append(getDiagonal(board, -1))

    for line in lines:
        if check_threat(line): # If the line is a threat
            threat_count += 1
    score += threat_count * 15 
    center_indices = [5, 6, 9, 10] # Indices of the 4 central squares
    center_control = 0 # Counts pieces in the center
    for i in center_indices:
        if board[i] is not None:
            center_control += 1

    score += center_control * 3 # Weight center control
    return score           

def negamax(state, player, depth, alpha=-float('inf'), beta=float('inf')):
    # Implements Negamax with alpha-beta pruning to find the best score for player_at_node
    def winnerF(board): # Winner def bur return Truf if win and False if lose
        for i in range(4):
            if same(getLine(board, i)):
                return True
            if same(getColumn(board, i)):
                return True
        if same(getDiagonal(board, 1)):
            return True
        return same(getDiagonal(board, -1))


    if winner(state) is int or isFull(state["board"]):
        return utility(state, player) # Use utility for true terminal states.


    if depth == 0 and isFull(state["board"]) is False: # heuristic call if depth is 0 
        return evaluate_heuristic(state, player) 



    value = -float('inf') # Stores the maximum score found for player_at_node.

    piece_to_place = state["piece"] # Piece player_at_node must place.
    board = deepcopy(state["board"]) # Work on a copy of the board.
    current_player_index_str = str(state["current"]) # Should be same as player_at_node.
    opponent_player_index_str = str(1 - int(current_player_index_str))


    placed_pieces_fs = {p for p in board if p is not None}
    if piece_to_place:
         placed_pieces_fs.add(piece_to_place) 

    # Determine available pieces to give to the opponent and position unused
    pieces = piece()
    res = []
    for i, elem in enumerate(state["board"]):
        if elem is None:
            res.append(i)
        if elem in pieces:
            pieces.remove(elem)
    empty_positions = res
    available_to_give = pieces 


    for i in empty_positions: # Iterate over possible placement positions
        new_board = list(board) # Create a aonther board for this move
        new_board[i] = piece_to_place # Place the piece


        if winnerF(new_board) is True: # If this placement wins for player_at_node

            value = max(value, float('inf'))

            alpha = max(alpha, value)
            if alpha >= beta:
                 return value # Pruning if win is found and good enough
            continue # Try next placement if not pruning


        # If not an immediate win, consider pieces to give to opponent
        if not available_to_give: # No pieces left to give.
             current_eval = 0 # Draw
        else:
             best_recursive_score = -float('inf')

             for next_piece_to_give in available_to_give:
                next_state = {
                    "players": state["players"],
                    "current": opponent_player_index_str, 
                    "board": tuple(new_board),
                    "piece": next_piece_to_give 
                }
                # Recursive call for opponent. Score is from opponent's view. Negate for player_at_node's view
                eval_opponent = -negamax(next_state, opponent_player_index_str, depth - 1, -beta, -alpha)
                best_recursive_score = max(best_recursive_score, eval_opponent)

             current_eval = best_recursive_score # Update best score for player_at_node.

        value = max(value, current_eval)

        alpha = max(alpha, value)
        if alpha >= beta:
            break 

    return value 

def find_best_negamax_move(state, player, depth):
    # Finds the best (position to place, piece to give) using Negamax evaluation
    best_score = -float('inf')
    best_move_pos = None
    best_piece_to_give = None

    piece_to_place = state["piece"] # Piece current `player` must place
    board = state["board"]
    current_player_index_str = str(state["current"])
    opponent_player_index_str = str(1 - int(current_player_index_str))
    # Determine available pieces to give and empty positions
    pieces = piece()
    res = []
    for i, elem in enumerate(state["board"]):
        if elem is None:
            res.append(i) # Add empty pos
        if elem in pieces:
            pieces.remove(elem) # Remove on-board pieces 
    try:
        pieces.remove(state["piece"]) # Check before removing
    except:
        random.choice(pieces)
    empty_positions = res
    available_to_give = pieces 

    if state["board"] == [None]*16 and state["piece"] is None: # Startint game useless to use AI
        return None, random.choice(pieces)
    
    if state["board"] == [None]*16 and state["piece"] is not None: # Second move useless to use AI
        return random.choice(res), random.choice(pieces)
    
    def winnerF(board):
        for i in range(4):
            if same(getLine(board, i)):
                return True
            if same(getColumn(board, i)):
                return True
        if same(getDiagonal(board, 1)):
            return True
        return same(getDiagonal(board, -1))
    
    if not empty_positions: return None, None # No place to move


    for i in empty_positions: # Iterate over possible placements
        new_board = list(board)
        new_board[i] = piece_to_place # Place the piece


        if winnerF(new_board) is True:
             move_score = float('inf')
             try:
                chosen_piece_for_next = random.choice(available_to_give)
             except:
                move_score = 0
                chosen_piece_for_next = None 
        else:

            temp_best_recursive_score = -float('inf')
            temp_chosen_piece = None
            for next_piece in available_to_give: # Try giving each available piece
                 next_state = {
                     "players": state["players"],
                     "current": opponent_player_index_str,
                     "board": tuple(new_board), 
                     "piece": next_piece
                 }
                # eval_opponent is score from opponent's view. Negate for player's view
                 eval_opponent = -negamax(next_state, opponent_player_index_str, depth - 1, -float('inf'), float('inf')) 


                 if eval_opponent > temp_best_recursive_score:
                     temp_best_recursive_score = eval_opponent
                     temp_chosen_piece = next_piece

            move_score = temp_best_recursive_score
            chosen_piece_for_next = temp_chosen_piece

        # Update overall best score and move found
        if move_score > best_score:
            best_score = move_score
            best_move_pos = i
            best_piece_to_give = chosen_piece_for_next

    # Security if bug in algorithm
    if best_piece_to_give is None and available_to_give: # If no piece chosen and pieces are available
        best_piece_to_give = next(iter(available_to_give)) # Pick first available 

    if best_move_pos is None and state["board"] != [None]*16: # If no position chosen and board not empty
         return random.choice(empty_positions), best_piece_to_give
    return best_move_pos, best_piece_to_give

def shufflepiece(piece_final):
    piece = list(piece_final)
    random.shuffle(piece)
    piece = ''.join(piece)
    return piece

import threading
def game(state,start_time):
    # Standardize input state
    state = deepcopy(state)
    state["piece"] = conversion_piece(state["piece"])
    state["board"] = [conversion_piece(p) for p in state["board"]]
    player = str(state["current"])
    
    # For regular game play, use threading with timeout
    
    # Flag to stop the calculation thread
    stop_calculation = threading.Event()
    def calculation_thread(result):
        try:
            # Start with depth 1 and increase gradually
            current_depth = 2
            empty_positions = [i for i in range(16) if state["board"][i] is None]
            if len(empty_positions) < 13:
                while not stop_calculation.is_set() and current_depth <= 15:  # Max depth 15
                    move = find_best_negamax_move(deepcopy(state), player, current_depth)
                    print(f'profondeur : {current_depth}')
                    if move[0] is not None:
                        result[0] = move[0]  # Position
                        result[1] = shufflepiece(move[1])  # Piece to give
                        
                    current_depth += 1
            else:
                move = find_best_negamax_move(deepcopy(state), player, current_depth)
                result[0] = move[0]  # Position
                result[1] = shufflepiece(move[1])  # Piece to give

        except Exception as e:
            print(f"Error in calculation thread: {e}")

    result = [None, None]  # Will store the final position and piece
    # Start the calculation thread
    thread = threading.Thread(target=calculation_thread, args=(result,))
    thread.daemon = True
    thread.start()
    # Wait for the thread with timeout
    thread.join(timeout=2.5)  # Slightly less than 3s to ensure safe return
    
    # Signal the thread to stop if it's still running
    stop_calculation.set()
    return result[0], result[1]  # No move possible
