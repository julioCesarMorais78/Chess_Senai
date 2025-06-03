"""
Chess Game with Tkinter GUI in Python + python-chess AI.

Como jogar:
- Execute este script com Python 3.
- Escolha o nível de dificuldade ao iniciar.
- Você joga de brancas, a máquina joga de pretas.
- Clique em uma peça para selecionar, depois clique em um destino válido.
- O jogo segue as regras do xadrez, com promoção automática para dama.
- Para sair, feche a janela.

Autor: BLACKBOXAI + GitHub Copilot
"""

import copy
import tkinter as tk
from tkinter import messagebox
import chess
import random


def pos_to_coords(pos):
    col = ord(pos[0].lower()) - ord('a')
    row = 8 - int(pos[1])
    return row, col


def coords_to_pos(row, col):
    return chr(col + ord('a')) + str(8 - row)


def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8


def line_moves(board, r, c, dr, dc, color):
    moves = []
    nr, nc = r + dr, c + dc
    while in_bounds(nr, nc):
        if board[nr][nc] is None:
            moves.append((nr, nc))
        elif board[nr][nc].color != color:
            moves.append((nr, nc))
            break
        else:
            break
        nr += dr
        nc += dc
    return moves


class Piece:
    def __init__(self, color):
        self.color = color
        self.name = '?'

    def possible_moves(self, board, r, c):
        return []

    def enemy_color(self):
        return 'black' if self.color == 'white' else 'white'

    def __str__(self):
        return self.name.upper() if self.color == 'white' else self.name.lower()

    def symbol(self):
        # Unicode chess symbols for better display in GUI
        symbols = {
            'K': {'white': '\u2654', 'black': '\u265A'},
            'Q': {'white': '\u2655', 'black': '\u265B'},
            'R': {'white': '\u2656', 'black': '\u265C'},
            'B': {'white': '\u2657', 'black': '\u265D'},
            'N': {'white': '\u2658', 'black': '\u265E'},
            'P': {'white': '\u2659', 'black': '\u265F'},
        }
        return symbols.get(self.name, {'white': '?', 'black': '?'}).get(self.color, '?')


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = 'P'

    def possible_moves(self, board, r, c):
        moves = []
        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1

        # Move forward
        if in_bounds(r + direction, c) and board[r + direction][c] is None:
            moves.append((r + direction, c))
            if r == start_row and board[r + 2*direction][c] is None:
                moves.append((r + 2*direction, c))

        # Captures
        for dc in [-1, 1]:
            nr, nc = r + direction, c + dc
            if in_bounds(nr, nc) and board[nr][nc] is not None and board[nr][nc].color == self.enemy_color():
                moves.append((nr, nc))

        return moves


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = 'R'

    def possible_moves(self, board, r, c):
        moves = []
        moves.extend(line_moves(board, r, c, -1, 0, self.color))
        moves.extend(line_moves(board, r, c, 1, 0, self.color))
        moves.extend(line_moves(board, r, c, 0, -1, self.color))
        moves.extend(line_moves(board, r, c, 0, 1, self.color))
        return moves


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = 'N'

    def possible_moves(self, board, r, c):
        moves = []
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                        (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in knight_moves:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc):
                target = board[nr][nc]
                if target is None or target.color == self.enemy_color():
                    moves.append((nr, nc))
        return moves


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = 'B'

    def possible_moves(self, board, r, c):
        moves = []
        moves.extend(line_moves(board, r, c, -1, -1, self.color))
        moves.extend(line_moves(board, r, c, -1, 1, self.color))
        moves.extend(line_moves(board, r, c, 1, -1, self.color))
        moves.extend(line_moves(board, r, c, 1, 1, self.color))
        return moves


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = 'Q'

    def possible_moves(self, board, r, c):
        moves = []
        moves.extend(line_moves(board, r, c, -1, 0, self.color))
        moves.extend(line_moves(board, r, c, 1, 0, self.color))
        moves.extend(line_moves(board, r, c, 0, -1, self.color))
        moves.extend(line_moves(board, r, c, 0, 1, self.color))
        moves.extend(line_moves(board, r, c, -1, -1, self.color))
        moves.extend(line_moves(board, r, c, -1, 1, self.color))
        moves.extend(line_moves(board, r, c, 1, -1, self.color))
        moves.extend(line_moves(board, r, c, 1, 1, self.color))
        return moves


class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = 'K'

    def possible_moves(self, board, r, c):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc):
                    target = board[nr][nc]
                    if target is None or target.color == self.enemy_color():
                        moves.append((nr, nc))
        return moves


class ChessGameGUI:
    def __init__(self, master):
        self.master = master
        master.title("Python Chess")

        self.difficulty = self.ask_difficulty()
        self.vs_ai = True  # Sempre contra a máquina neste exemplo

        self.chess_board = chess.Board()
        self.board = self.create_start_board()
        self.player_turn = 'white'
        self.move_history = []
        self.selected = None  # Selected square (r, c)
        self.possible_moves = []

        self.squares = [[None for _ in range(8)] for _ in range(8)]

        self.create_widgets()
        self.draw_board()

    def ask_difficulty(self):
        difficulties = ["Fácil", "Médio", "Difícil"]
        self.diff_var = tk.StringVar(value=difficulties[0])
        popup = tk.Toplevel()
        popup.title("Escolha a dificuldade")
        tk.Label(popup, text="Selecione o nível:").pack()
        for d in difficulties:
            tk.Radiobutton(popup, text=d, variable=self.diff_var, value=d).pack(anchor='w')
        tk.Button(popup, text="OK", command=popup.destroy).pack()
        self.master.wait_window(popup)
        return self.diff_var.get()

    def create_start_board(self):
        board = [[None]*8 for _ in range(8)]

        # Pawns
        for c in range(8):
            board[6][c] = Pawn('white')
            board[1][c] = Pawn('black')

        # Rooks
        board[7][0] = Rook('white')
        board[7][7] = Rook('white')
        board[0][0] = Rook('black')
        board[0][7] = Rook('black')

        # Knights
        board[7][1] = Knight('white')
        board[7][6] = Knight('white')
        board[0][1] = Knight('black')
        board[0][6] = Knight('black')

        # Bishops
        board[7][2] = Bishop('white')
        board[7][5] = Bishop('white')
        board[0][2] = Bishop('black')
        board[0][5] = Bishop('black')

        # Queens
        board[7][3] = Queen('white')
        board[0][3] = Queen('black')

        # Kings
        board[7][4] = King('white')
        board[0][4] = King('black')

        return board

    def create_widgets(self):
        self.frame = tk.Frame(self.master)
        self.frame.pack()

        for r in range(8):
            for c in range(8):
                color = self.get_square_color(r, c)
                btn = tk.Button(self.frame, text='', font=('Arial', 40), width=3, height=1,
                                bg=color, fg='black',
                                command=lambda r=r, c=c: self.on_square_click(
                                    r, c),
                                relief='flat')
                btn.grid(row=r, column=c)
                self.squares[r][c] = btn

        self.status_label = tk.Label(
            self.master, text='White to move', font=('Arial', 16))
        self.status_label.pack(pady=10)

    def get_square_color(self, r, c):
        return '#F0D9B5' if (r+c) % 2 == 0 else '#B58863'

    def draw_board(self):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                btn = self.squares[r][c]
                if piece is None:
                    btn.config(text='')
                else:
                    btn.config(text=piece.symbol(),
                               fg='black' if piece.color == 'black' else 'white')
                btn.config(bg=self.get_square_color(r, c))
        self.highlight_moves()

    def highlight_moves(self):
        # Highlight possible moves in yellow
        for r, c in self.possible_moves:
            self.squares[r][c].config(bg='yellow')

        # Highlight selected in orange
        if self.selected is not None:
            sr, sc = self.selected
            self.squares[sr][sc].config(bg='orange')

    def is_move_legal(self, start_r, start_c, end_r, end_c):
        piece = self.board[start_r][start_c]
        if piece is None:
            return False, "No piece at start position"
        if piece.color != self.player_turn:
            return False, "It's not your turn"
        moves = piece.possible_moves(self.board, start_r, start_c)
        if (end_r, end_c) not in moves:
            return False, "Illegal move for that piece"

        board_copy = copy.deepcopy(self.board)
        board_copy[end_r][end_c] = board_copy[start_r][start_c]
        board_copy[start_r][start_c] = None
        if self.is_in_check(board_copy, self.player_turn):
            return False, "You cannot move into check"
        return True, ""

    def make_move(self, start_r, start_c, end_r, end_c):
        piece = self.board[start_r][start_c]
        self.board[end_r][end_c] = piece
        self.board[start_r][start_c] = None
        self.move_history.append((start_r, start_c, end_r, end_c, piece))

        # Pawn promotion (auto queen)
        if isinstance(piece, Pawn) and (end_r == 0 or end_r == 7):
            self.board[end_r][end_c] = Queen(piece.color)

        # Atualiza também o objeto python-chess
        move_uci = coords_to_pos(start_r, start_c) + coords_to_pos(end_r, end_c)
        # Promoção
        if isinstance(piece, Pawn) and (end_r == 0 or end_r == 7):
            move_uci += 'q'
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.chess_board.legal_moves:
                self.chess_board.push(move)
        except Exception:
            pass

    def is_in_check(self, board, color):
        king_pos = None
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p is not None and isinstance(p, King) and p.color == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        if king_pos is None:
            return True

        enemy_color = 'black' if color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p is not None and p.color == enemy_color:
                    moves = p.possible_moves(board, r, c)
                    if king_pos in moves:
                        return True
        return False

    def has_valid_moves(self, color):
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p is not None and p.color == color:
                    moves = p.possible_moves(self.board, r, c)
                    for (nr, nc) in moves:
                        board_copy = copy.deepcopy(self.board)
                        board_copy[nr][nc] = board_copy[r][c]
                        board_copy[r][c] = None
                        if not self.is_in_check(board_copy, color):
                            return True
        return False

    def switch_turn(self):
        self.player_turn = 'black' if self.player_turn == 'white' else 'white'
        self.status_label.config(
            text=f"{self.player_turn.capitalize()} to move")

    def on_square_click(self, r, c):
        if self.vs_ai and self.player_turn == 'black':
            return  # Ignora clique quando é a vez da máquina
        piece = self.board[r][c]
        if self.selected is None:
            # Select a piece only if it's the player's turn color
            if piece is not None and piece.color == self.player_turn:
                self.selected = (r, c)
                self.possible_moves = self.get_legal_moves_for_selected()
                self.draw_board()
        else:
            # Clicking a square to move or reselect
            if (r, c) == self.selected:
                # Deselect
                self.selected = None
                self.possible_moves = []
                self.draw_board()
            elif (r, c) in self.possible_moves:
                start_r, start_c = self.selected
                legal, msg = self.is_move_legal(start_r, start_c, r, c)
                if legal:
                    self.make_move(start_r, start_c, r, c)
                    self.selected = None
                    self.possible_moves = []
                    self.switch_turn()
                    self.draw_board()
                    self.check_game_end()
                    if self.vs_ai and self.player_turn == 'black':
                        self.master.after(500, self.ai_move)
                else:
                    messagebox.showinfo("Illegal move", msg)
            else:
                # New selection if clicked on own piece
                if piece is not None and piece.color == self.player_turn:
                    self.selected = (r, c)
                    self.possible_moves = self.get_legal_moves_for_selected()
                    self.draw_board()
                else:
                    # Invalid click, ignore
                    pass

    def get_legal_moves_for_selected(self):
        sr, sc = self.selected
        piece = self.board[sr][sc]
        moves_raw = piece.possible_moves(self.board, sr, sc)
        legal_moves = []
        for (nr, nc) in moves_raw:
            board_copy = copy.deepcopy(self.board)
            board_copy[nr][nc] = board_copy[sr][sc]
            board_copy[sr][sc] = None
            if not self.is_in_check(board_copy, self.player_turn):
                legal_moves.append((nr, nc))
        return legal_moves

    def check_game_end(self):
        if self.is_in_check(self.board, self.player_turn):
            if not self.has_valid_moves(self.player_turn):
                messagebox.showinfo("Checkmate", f"Checkmate! {self.player_turn.capitalize()} perde.")
                self.master.destroy()
            else:
                messagebox.showinfo("Check", "Check!")
        else:
            if not self.has_valid_moves(self.player_turn):
                messagebox.showinfo("Stalemate", "Empate! Fim de jogo.")
                self.master.destroy()

    def ai_move(self):
        legal_moves = list(self.chess_board.legal_moves)
        if not legal_moves:
            return
        move = self.choose_ai_move(legal_moves)
        self.chess_board.push(move)
        self.update_board_from_chess()
        self.switch_turn()
        self.draw_board()
        self.check_game_end()

    def choose_ai_move(self, legal_moves):
        if self.difficulty == "Fácil":
            return random.choice(legal_moves)
        elif self.difficulty == "Médio":
            captures = [m for m in legal_moves if self.chess_board.is_capture(m)]
            return random.choice(captures) if captures else random.choice(legal_moves)
        else:  # Difícil
            best_move = None
            best_score = -9999
            for move in legal_moves:
                self.chess_board.push(move)
                score = self.evaluate_board()
                self.chess_board.pop()
                if score > best_score:
                    best_score = score
                    best_move = move
            return best_move if best_move else random.choice(legal_moves)

    def evaluate_board(self):
        piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
        score = 0
        for piece_type in piece_values:
            score += len(self.chess_board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]
            score -= len(self.chess_board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        return score

    def update_board_from_chess(self):
        # Atualiza self.board a partir do FEN do python-chess
        fen = self.chess_board.board_fen()
        rows = fen.split('/')
        for r in range(8):
            row = rows[r]
            c = 0
            for ch in row:
                if ch.isdigit():
                    for _ in range(int(ch)):
                        self.board[r][c] = None
                        c += 1
                else:
                    color = 'white' if ch.isupper() else 'black'
                    piece_type = ch.lower()
                    if piece_type == 'p':
                        self.board[r][c] = Pawn(color)
                    elif piece_type == 'r':
                        self.board[r][c] = Rook(color)
                    elif piece_type == 'n':
                        self.board[r][c] = Knight(color)
                    elif piece_type == 'b':
                        self.board[r][c] = Bishop(color)
                    elif piece_type == 'q':
                        self.board[r][c] = Queen(color)
                    elif piece_type == 'k':
                        self.board[r][c] = King(color)
                    c += 1


if __name__ == '__main__':
    root = tk.Tk()
    game = ChessGameGUI(root)
    root.mainloop()