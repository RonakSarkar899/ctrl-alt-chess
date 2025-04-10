import tkinter as tk
import chess
import chess.engine
from tkinter import messagebox
import os

board = chess.Board()

STOCKFISH_PATH = "C:\\Users\\debab\\Downloads\\stockfish-windows-x86-64-avx2\\stockfish\\stockfish-windows-x86-64-avx2.exe"

class ChessApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess - Player vs Computer")
        self.canvas = tk.Canvas(self.master, width=520, height=520)
        self.canvas.pack()
        self.drag_data = {"piece_id": None, "from_square": None, "from_coords": None, "symbol": None}

        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        except Exception as e:
            messagebox.showerror("Engine Error", f"Could not start engine: {e}")
            self.master.destroy()
            return

        self.draw_board()

        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.do_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)

    def draw_board(self):
        self.canvas.delete("square")
        for row in range(8):
            for col in range(8):
                x1, y1 = col * 65, row * 65
                x2, y2 = x1 + 65, y1 + 65
                color = "#F0D9B5" if (row + col) % 2 == 0 else "#B58863"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="square")
        self.refresh_board()

    def refresh_board(self, skip_square=None):
        self.canvas.delete("piece")
        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)
                if square == skip_square:
                    continue
                piece = board.piece_at(square)
                if piece:
                    x1, y1 = col * 65, row * 65
                    tag = f"piece_{col}_{7 - row}"
                    self.canvas.create_text(
                        x1 + 32, y1 + 32,
                        text=self.get_unicode(piece),
                        font=("Segoe UI Symbol", 32),
                        tags=("piece", tag)
                    )

    def get_unicode(self, piece):
        symbols = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
        }
        return symbols[piece.symbol()]

    def start_drag(self, event):
        if board.is_game_over():
            return

        col = event.x // 65
        row = 7 - (event.y // 65)
        square = chess.square(col, row)
        piece = board.piece_at(square)

        if piece and piece.color == chess.WHITE:
            self.drag_data["from_square"] = square
            self.drag_data["from_coords"] = (event.x, event.y)
            self.drag_data["symbol"] = self.get_unicode(piece)
            self.refresh_board(skip_square=square)

            # Draw temporary dragged piece at click position
            self.drag_data["piece_id"] = self.canvas.create_text(
                event.x, event.y,
                text=self.drag_data["symbol"],
                font=("Segoe UI Symbol", 32),
                tags="dragged_piece"
            )
            self.canvas.tag_raise(self.drag_data["piece_id"])

    def do_drag(self, event):
        if self.drag_data["piece_id"]:
            self.canvas.coords(self.drag_data["piece_id"], event.x, event.y)

    def end_drag(self, event):
        if not self.drag_data["piece_id"]:
            return

        to_col = event.x // 65
        to_row = 7 - (event.y // 65)
        to_square = chess.square(to_col, to_row)
        move = chess.Move(self.drag_data["from_square"], to_square)

        self.canvas.delete(self.drag_data["piece_id"])

        if move in board.legal_moves:
            board.push(move)
            self.draw_board()
            self.master.after(500, self.computer_move)
        else:
            self.refresh_board()

        self.drag_data = {"piece_id": None, "from_square": None, "from_coords": None, "symbol": None}

    def computer_move(self):
        if board.is_game_over():
            messagebox.showinfo("Game Over", board.result())
            return

        result = self.engine.play(board, chess.engine.Limit(time=0.1))
        board.push(result.move)
        self.draw_board()

        if board.is_game_over():
            messagebox.showinfo("Game Over", board.result())

    def on_closing(self):
        if hasattr(self, 'engine'):
            self.engine.quit()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()