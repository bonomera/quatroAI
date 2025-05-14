# AI Move Strategy

This document outlines how the AI in this project decides on its next move in a Quarto-like board game. The goal is to select the best position on the board to place a piece and the best piece to then give to the opponent.

## How the AI Chooses a Move

The AI uses a strategy that combines looking ahead at possible future moves and evaluating how good the current board situation is.

1.  **Understanding the Game State:**
    *   The AI knows the current 4x4 board, which piece it *must* place (given by the opponent), and whose turn it is.
    *   Each game piece has four distinct attributes (e.g., Big/Small, Light/Dark, Empty/Full, Square/Circle). A winning line is four pieces in a row, column, or diagonal that share at least one common attribute.

2.  **Exploring Possibilities (Negamax Algorithm):**
    *   The decision-making uses the **Negamax** algorithm with **alpha-beta pruning**. This is a way to explore a tree of possible future moves.
    *   The AI "thinks" several moves ahead (this is called the search `depth`).

3.  **Evaluating Board Positions:**
    For each potential future board state it considers, the AI calculates a score:
    *   **Immediate Win/Loss:** If placing a piece results in a win for the AI, that move gets a very high score. If it leads to a loss (e.g., the opponent can win immediately after), it gets a very low score.
    *   **Heuristic Evaluation (`evaluate_heuristic`):** For positions that are not immediate wins or losses, a special function estimates how good the board is. This "heuristic" generally gives higher scores to:
        *   Creating lines of three pieces that share a common attribute (a "threat" because one more piece could win).
        *   Having pieces placed in the central squares of the board.

4.  **The Two-Part Move:**
    A player's turn has two parts:
    *   **Placing a Piece:** The AI considers all empty spots on the board where it can place the piece it was given.
    *   **Giving a Piece:** For *each* possible placement, the AI then considers every remaining unplayed piece it could give to the opponent.

5.  **Making the Final Decision (`find_best_negamax_move`):**
    *   For every possible placement of its current piece, the AI simulates giving each available *next piece* to the opponent.
    *   It then uses Negamax to estimate the score of the board *after* the opponent makes their best reply (using the piece the AI just gave them).
    *   The AI chooses the initial placement and the piece-to-give combination that leads to the highest possible score for itself, assuming the opponent will also play optimally.
    *   Alpha-beta pruning helps to speed up this search by intelligently ignoring branches of future moves that are unlikely to be the best.

6.  **Putting It Together (`game` function):**
    The main `game` function sets an appropriate search depth (how many moves to look ahead, which can change slightly as the game progresses) and then calls `find_best_negamax_move` to get the chosen position and the piece to give to the opponent.

In short, the AI tries to find a move (a position to place its current piece and a new piece to give the opponent) that maximizes its chances of winning or improving its board position, while assuming the opponent will also play smartly.

## Python Libraries Used

The project uses the following Python libraries:

* `pytest` — to run tests.
* `unittest.mock` — to mock functions, files, and sockets during testing.
* `socket` — for connecting to the game server and handling communication.
* `json` — for encoding and decoding game messages.
* `os` — for file path handling.
* `time` — to measure the time taken by the AI to make decisions.
* `threading` — to run the local server alongside the main client logic.
* `random` — to shuffle the list of available pieces and add randomness.
* `copy`, `deepcopy` — to duplicate game states during the AI’s search process.

## Student ID (matricule)

Im alone, my ID : 23383
