import pyglet
import numpy as np
import random
import math

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4


def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if (
                board[r][c] == piece
                and board[r][c + 1] == piece
                and board[r][c + 2] == piece
                and board[r][c + 3] == piece
            ):
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c] == piece
                and board[r + 2][c] == piece
                and board[r + 3][c] == piece
            ):
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c + 1] == piece
                and board[r + 2][c + 2] == piece
                and board[r + 3][c + 3] == piece
            ):
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if (
                board[r][c] == piece
                and board[r - 1][c + 1] == piece
                and board[r - 2][c + 2] == piece
                and board[r - 3][c + 3] == piece
            ):
                return True


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c : c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r : r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score positive sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(board):
    return (
        winning_move(board, PLAYER_PIECE)
        or winning_move(board, AI_PIECE)
        or len(get_valid_locations(board)) == 0
    )


def minimax(board, depth, alpha, beta, maximizingPlayer, difficulty):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False, difficulty)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True, difficulty)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


def pick_best_move(board, piece, difficulty):
    depth = 0
    if difficulty == "easy":
        depth = 1
    elif difficulty == "medium":
        depth = 3
    elif difficulty == "hard":
        depth = 5

    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = minimax(temp_board, depth, -math.inf, math.inf, False, difficulty)[1]
        if score > best_score:
            best_score = score
            best_col = col

    return best_col


class ConnectFourUI(pyglet.window.Window):
    def __init__(self):
        super().__init__(800, 600, caption="Connect Four")

        self.current_screen = "difficulty_selection"
        self.difficulty = None

        self.board = create_board()
        self.current_player = PLAYER_PIECE

        self.hover_column = None
        self.game_over = False

    def on_draw(self):
        self.clear()
        if self.current_screen == "difficulty_selection":
            self.draw_difficulty_selection_screen()
        elif self.current_screen == "game_board":
            self.draw_game_board()

    def draw_difficulty_selection_screen(self):
        pyglet.gl.glClearColor(0.5, 0.5, 0.5, 1.0)  # Darker background
        label = pyglet.text.Label(
            "Choose a difficulty:",
            font_name="Arial",
            font_size=36,
            x=self.width // 2,
            y=self.height // 2,
            anchor_x="center",
            anchor_y="center",
        )
        label.draw()

        easy_button = pyglet.shapes.Rectangle(200, 200, 100, 50, color=(0, 255, 0))
        easy_button.label = pyglet.text.Label(
            "Easy",
            font_name="Arial",
            font_size=24,
            x=250,
            y=225,
            anchor_x="center",
            anchor_y="center",
        )
        easy_button.draw()

        medium_button = pyglet.shapes.Rectangle(350, 200, 100, 50, color=(255, 255, 0))
        medium_button.label = pyglet.text.Label(
            "Medium",
            font_name="Arial",
            font_size=24,
            x=400,
            y=225,
            anchor_x="center",
            anchor_y="center",
        )
        medium_button.draw()

        hard_button = pyglet.shapes.Rectangle(500, 200, 100, 50, color=(255, 0, 0))
        hard_button.label = pyglet.text.Label(
            "Hard",
            font_name="Arial",
            font_size=24,
            x=550,
            y=225,
            anchor_x="center",
            anchor_y="center",
        )
        hard_button.draw()

    def draw_game_board(self):
        pyglet.gl.glClearColor(0.3, 0.3, 0.3, 1.0)  # Darker background
        # Draw the grid
        for row in range(ROW_COUNT):
            for col in range(COLUMN_COUNT):
                pyglet.shapes.Rectangle(
                    100 + col * 80, 100 + row * 80, 60, 60, color=(100, 100, 100)
                ).draw()  # Darker grid
                if self.board[row][col] == PLAYER_PIECE:
                    pyglet.shapes.Circle(
                        130 + col * 80, 130 + row * 80, 25, color=(255, 0, 0)
                    ).draw()
                elif self.board[row][col] == AI_PIECE:
                    pyglet.shapes.Circle(
                        130 + col * 80, 130 + row * 80, 25, color=(255, 255, 0)
                    ).draw()

        if self.hover_column is not None:
            pyglet.shapes.Rectangle(
                100 + self.hover_column * 80, 100, 60, 480, color=(255, 255, 255, 100)
            ).draw()  # Semi-transparent rectangle

    def on_mouse_motion(self, x, y, dx, dy):
        if self.current_screen == "game_board":
            self.hover_column = (
                (x - 100) // 80 if 100 <= x <= 680 and 100 <= y <= 580 else None
            )

    def on_mouse_press(self, x, y, button, modifiers):
        if self.current_screen == "difficulty_selection":
            if 200 <= x <= 300 and 200 <= y <= 250:
                self.difficulty = "easy"
                self.current_screen = "game_board"
            elif 350 <= x <= 450 and 200 <= y <= 250:
                self.difficulty = "medium"
                self.current_screen = "game_board"
            elif 500 <= x <= 600 and 200 <= y <= 250:
                self.difficulty = "hard"
                self.current_screen = "game_board"
        elif self.current_screen == "game_board" and not self.game_over:
            if self.hover_column is not None:
                self.drop_piece(self.hover_column)

    def drop_piece(self, col):
        row = get_next_open_row(self.board, col)
        if row is not None:
            drop_piece(self.board, row, col, PLAYER_PIECE)
            if not winning_move(self.board, PLAYER_PIECE):
                ai_col = pick_best_move(self.board, AI_PIECE, self.difficulty)
                ai_row = get_next_open_row(self.board, ai_col)
                if ai_row is not None:
                    drop_piece(self.board, ai_row, ai_col, AI_PIECE)
            if winning_move(self.board, PLAYER_PIECE):
                print("Player wins!")
                self.game_over = True
            elif winning_move(self.board, AI_PIECE):
                print("AI wins!")
                self.game_over = True


if __name__ == "__main__":
    window = ConnectFourUI()
    pyglet.app.run()
