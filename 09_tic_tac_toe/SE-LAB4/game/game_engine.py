"""
GameEngine: owns the board, turn state, round-end logic, scoreboard,
first-player choice, and restart controls.
"""

from game.rules import check_winner, is_board_full
from game.renderer import board_pos_to_cell
from game.ai import choose_move

HUMAN_SYMBOL = 'X'
COMPUTER_SYMBOL = 'O'


class GameEngine:
    def __init__(self):
        # First player for the current round.
        self.first_player = HUMAN_SYMBOL

        # Current round state
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = self.first_player
        self.round_over = False
        self.winner = None

        # Persistent match scoreboard
        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0

    def handle_click(self, pos):
        # Do not accept moves after the round has ended.
        if self.round_over:
            return

        # Only the human can make a mouse click move.
        if self.current_player != HUMAN_SYMBOL:
            return

        cell = board_pos_to_cell(pos)
        if cell is None:
            return

        row, col = cell

        # Task 3: reject occupied cells.
        if self.board[row][col] is not None:
            return

        self.board[row][col] = self.current_player

        self.check_round_end()

        # Do not change turns if the round ended.
        if self.round_over:
            return

        self.current_player = COMPUTER_SYMBOL
        self._maybe_take_computer_turn()

    def _maybe_take_computer_turn(self):
        # Computer only moves when it is O's turn.
        if self.round_over or self.current_player != COMPUTER_SYMBOL:
            return

        move = choose_move(self.board)

        if move is None:
            return

        row, col = move

        # Do not overwrite an occupied cell.
        if self.board[row][col] is not None:
            return

        self.board[row][col] = COMPUTER_SYMBOL

        self.check_round_end()

        # Do not change turns if the round ended.
        if self.round_over:
            return

        self.current_player = HUMAN_SYMBOL

    def start_round(self, first_player=None):
        """
        Start a new round without changing the scoreboard.

        X = human starts.
        O = computer starts.
        """

        if first_player is not None:
            if first_player not in (HUMAN_SYMBOL, COMPUTER_SYMBOL):
                return

            self.first_player = first_player

        # Reset only the current round.
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = self.first_player
        self.round_over = False
        self.winner = None

        # If O starts, the computer moves automatically.
        self._maybe_take_computer_turn()

    def restart_round(self):
        """
        Restart only the current round.
        The scoreboard is preserved.
        """
        self.start_round()

    def reset_match(self):
        """
        Reset the entire match.
        This clears the scoreboard and starts a fresh round.
        """

        # Clear scoreboard.
        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0

        # Reset starter to X.
        self.first_player = HUMAN_SYMBOL

        # Reset current round.
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = HUMAN_SYMBOL
        self.round_over = False
        self.winner = None

    def set_first_player(self, player):
        """
        Set who starts the next/current round.

        X = human starts.
        O = computer starts.
        """

        if player not in (HUMAN_SYMBOL, COMPUTER_SYMBOL):
            return

        self.first_player = player
        self.start_round()

    def handle_keydown(self, key):
        import pygame

        # R = restart current round.
        # Scoreboard is preserved.
        if key == pygame.K_r:
            self.restart_round()

        # M = reset entire match.
        # Scoreboard is cleared.
        elif key == pygame.K_m:
            self.reset_match()

        # X = X starts.
        elif key == pygame.K_x:
            self.set_first_player(HUMAN_SYMBOL)

        # O = O starts.
        elif key == pygame.K_o:
            self.set_first_player(COMPUTER_SYMBOL)

    def check_round_end(self):
        """
        Check whether the current round has ended.

        Winner is checked before draw so a winning final move
        is always counted as a win.
        """

        winner = check_winner(self.board)

        if winner:
            self.round_over = True
            self.winner = winner

            # Update the appropriate scoreboard exactly once.
            if winner == HUMAN_SYMBOL:
                self.x_wins += 1
            elif winner == COMPUTER_SYMBOL:
                self.o_wins += 1

            return

        # If there is no winner and the board is full, it is a draw.
        if is_board_full(self.board):
            self.round_over = True
            self.winner = None
            self.draws += 1

    def draw(self, surface, font):
        from game import renderer

        # Draw board.
        renderer.draw_board(surface, self.board)

        # Persistent scoreboard.
        scoreboard_text = (
            f"X Wins: {self.x_wins}    "
            f"O Wins: {self.o_wins}    "
            f"Draws: {self.draws}"
        )

        renderer.draw_text(
            surface,
            font,
            scoreboard_text,
            (10, 20)
        )

        # Current turn.
        turn_label = (
            "Your turn (X)"
            if self.current_player == HUMAN_SYMBOL
            else "Computer's turn (O)"
        )

        renderer.draw_text(
            surface,
            font,
            turn_label,
            (10, 50)
        )

        # Controls.
        controls = (
            "X/O: choose starter    "
            "R: restart round    "
            "M: reset match"
        )

        renderer.draw_text(
            surface,
            font,
            controls,
            (10, 80)
        )

        # Round result.
        if self.round_over:
            text = f"{self.winner} wins!" if self.winner else "Draw!"

            renderer.draw_banner(
                surface,
                font,
                text
            )