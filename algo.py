import random
import copy
import time
from copy import deepcopy
def board_into_int(state):
    return [None if x == 'None' or x is None else x for x in state["board"]]

def piece():
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
    if piecen in piece():
        return piecen
    if piecen is None:
        return None
    else:
        piecen = list(piecen)
        for i in piecen:
            if i in ['B', 'S']:
                tailles = i 
            if i in ['L', 'D']:
                couleurs = i
            if i in ['E', 'F']:
                remplissages = i
            if i in ['P', 'C']:
                formes = i
        piece_final = tailles + couleurs + remplissages + formes
    return piece_final

def same(L):
    if None in L:
        return False
    common = frozenset(L[0])
    for elem in L[1:]:
        common = common & frozenset(elem)
    return len(common) > 0


def getLine(board, i):
    return board[i * 4 : (i + 1) * 4]


def getColumn(board, j):
    return [board[i] for i in range(j, 16, 4)]


# dir == 1 or -1
def getDiagonal(board, dir):
    start = 0 if dir == 1 else 2
    return [board[start + i * (4 + dir)] for i in range(4)]


def winner(board):
    player = currentPlayer(board)
    board = board["board"]
    for i in range(4):
        if same(getLine(board, i)):
            return player
        if same(getColumn(board, i)):
            return player
    if same(getDiagonal(board, 1)):
        return player
    return same(getDiagonal(board, -1))

def utility(state, player):
	theWinner = winner(state)
	if theWinner is False and isFull(state) is True:
		return 0
	if theWinner == player:
		return float('inf')
	return -float('inf')

def gameOver(state):
	if winner(state) is str:
		return True

	empty = 0
	for elem in state:
		if elem is None:
			empty += 1
	return empty == 0

def currentPlayer(state):

    return state["current"]
def isFull(board):
    for elem in board:
        if elem is None:
            return False
    return True

def moves(state):
    pieces = piece()
    res = []
    for i, elem in enumerate(state):
        if elem is None:
            res.append(i)
        if elem in pieces:
            pieces.remove(elem)
          
    random.shuffle(res)
    return res

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
    pieces = [p for p in line if p is not None]
    if len(pieces) == 3:
        common_attributes = pieces[0] & pieces[1] & pieces[2]
        return len(common_attributes) > 0
    return False

def evaluate_heuristic(state, player):
    board = state["board"]
    score = 0

    threat_count = 0
    lines = []


    for i in range(4):
        lines.append(getLine(board, i))
        lines.append(getColumn(board, i))
    lines.append(getDiagonal(board, 1))
    lines.append(getDiagonal(board, -1))

    for line in lines:
        if check_threat(line):
            threat_count += 1

 

    score += threat_count * 15 


    center_indices = [5, 6, 9, 10]
    center_control = 0
    for i in center_indices:
        if board[i] is not None:
            center_control += 1

    score += center_control * 3 
    return score           

def negamax(state, player, depth, alpha=-float('inf'), beta=float('inf')):
    """Version corrigée de Negamax utilisant l'heuristique."""
    def winnerF(board):
        for i in range(4):
            if same(getLine(board, i)):
                return True
            if same(getColumn(board, i)):
                return True
        if same(getDiagonal(board, 1)):
            return True
        return same(getDiagonal(board, -1))


    if winner(state) is int or isFull(state["board"]) or depth == 0:
        return utility(state, player)


    if depth == 0 and isFull(state["board"]) is False:
        return evaluate_heuristic(state, player) 



    value = -float('inf')


    piece_to_place = state["piece"]
    board = deepcopy(state["board"])
    current_player_index_str = str(state["current"])
    opponent_player_index_str = str(1 - int(current_player_index_str))


    placed_pieces_fs = {p for p in board if p is not None}
    if piece_to_place:
         placed_pieces_fs.add(piece_to_place) 

    pieces = piece()
    res = []
    for i, elem in enumerate(state["board"]):
        if elem is None:
            res.append(i)
        if elem in pieces:
            pieces.remove(elem)
    empty_positions = res
    available_to_give = pieces 


    for i in empty_positions:
        new_board = list(board) 
        new_board[i] = piece_to_place 


        if winnerF(new_board) is True:

            value = max(value, float('inf'))

            alpha = max(alpha, value)
            if alpha >= beta:
                 return value 
            continue 


        if not available_to_give: 
             current_eval = 0 
        else:
             best_recursive_score = -float('inf')

             for next_piece_to_give in available_to_give:
                next_state = {
                    "players": state["players"],
                    "current": opponent_player_index_str, 
                    "board": tuple(new_board),
                    "piece": next_piece_to_give 
                }
                eval_opponent = -negamax(next_state, opponent_player_index_str, depth - 1, -beta, -alpha)
                best_recursive_score = max(best_recursive_score, eval_opponent)

             current_eval = best_recursive_score 

        value = max(value, current_eval)

        alpha = max(alpha, value)
        if alpha >= beta:
            break 

    return value 
def find_best_negamax_move(state, player, depth, start_time):
    best_score = -float('inf')
    best_move_pos = None
    best_piece_to_give = None

    piece_to_place = state["piece"]
    board = state["board"]
    current_player_index_str = str(state["current"])
    opponent_player_index_str = str(1 - int(current_player_index_str))

    pieces = piece()
    res = []
    for i, elem in enumerate(state["board"]):
        if elem is None:
            res.append(i)
        if elem in pieces:
            pieces.remove(elem)
    try:
        pieces.remove(state["piece"])
    except:
        random.choice(pieces)
    empty_positions = res
    available_to_give = pieces 
    if state["board"] == [None]*16 and state["piece"] is None:
        
        return None, random.choice(pieces)
    if state["board"] == [None]*16 and state["piece"] is not None:
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
    
    if not empty_positions: return None, None 


    for i in empty_positions:
        new_board = list(board)
        new_board[i] = piece_to_place


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
            for next_piece in available_to_give:
                 next_state = {
                     "players": state["players"],
                     "current": opponent_player_index_str,
                     "board": tuple(new_board), 
                     "piece": next_piece
                 }
                 
                 eval_opponent = -negamax(next_state, opponent_player_index_str, depth - 1, -float('inf'), float('inf')) # inversion des données


                 if eval_opponent > temp_best_recursive_score:
                     temp_best_recursive_score = eval_opponent
                     temp_chosen_piece = next_piece

            move_score = temp_best_recursive_score
            chosen_piece_for_next = temp_chosen_piece


        if move_score > best_score:
            best_score = move_score
            best_move_pos = i
            best_piece_to_give = chosen_piece_for_next


    if best_piece_to_give is None and available_to_give:
        best_piece_to_give = next(iter(available_to_give))

    if best_move_pos is None and state["board"] != [None]*16:
         return random.choice(empty_positions), best_piece_to_give
    return best_move_pos, best_piece_to_give

'''def game(state):
    start_time = time.time()
    state["piece"] = conversion_piece(state["piece"])
    player = str(state["current"])
    depth = 20
    depthgrowth = 0
    for i in state["board"]:
        if i is not None:
            depthgrowth += 1
    if 10 > depthgrowth >= 7:
        depth += 1
    if 14 > depthgrowth >= 10:
        depth = 8
    pos, piece_give = find_best_negamax_move(state, player, depth, start_time)
    # Derniere verification
    return pos, piece_give'''

def game(state):
    depth = 2
    depthgrowth = 0
    for i in state["board"]:
        if i is not None:
            depthgrowth += 1
    if 10 > depthgrowth >= 7:
        depth += 1
    if 14 > depthgrowth >= 10:
        depth = 8
    start_time = time.time()
    state = deepcopy(state)
    state["piece"] = conversion_piece(state["piece"])
    boardreal = []
    for i in state["board"]:
        boardreal.append(conversion_piece(i))
    
    state["board"] = boardreal
    player = str(state["current"])
    print(state)
    pos, piece_give = find_best_negamax_move(state, player, depth, start_time)
    return pos, piece_give
