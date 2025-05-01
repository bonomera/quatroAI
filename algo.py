def game(state_game): # Retrieve the game state to facilitate AI decision-making
    status = {
        "player": state_game.get('player'),
        "current_player": state_game.get('current'),
        "board": state_game.get('board'),
        "piece": state_game.get('piece')
    }
    pass