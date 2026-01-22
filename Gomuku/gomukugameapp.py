from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

class GomokuGame:
    def __init__(self, m=15, n=15):
        self.m = m
        self.n = n
        self.board = [[' ']*n for _ in range(m)]
        # Track last human move to use in your original blocking logic
        self.input_row = 0
        self.input_col = 0

    def row_check(self, r, c, stone):
        n_after, col = 0, c + 1
        while col < self.n and self.board[r][col] == stone:
            n_after += 1; col += 1
        n_before, col = 0, c - 1
        while col >= 0 and self.board[r][col] == stone:
            n_before += 1; col -= 1
        return n_after + n_before + 1

    def col_check(self, r, c, stone):
        n_after, row = 0, r + 1
        while row < self.m and self.board[row][c] == stone:
            n_after += 1; row += 1
        n_before, row = 0, r - 1
        while row >= 0 and self.board[row][c] == stone:
            n_before += 1; row -= 1
        return n_after + n_before + 1

    def right_diag_check(self, r, c, stone):
        n_after, row, col = 0, r + 1, c + 1
        while row < self.m and col < self.n and self.board[row][col] == stone:
            n_after += 1; row += 1; col += 1
        n_before, row, col = 0, r - 1, c - 1
        while row >= 0 and col >= 0 and self.board[row][col] == stone:
            n_before += 1; row -= 1; col -= 1
        return n_after + n_before + 1

    def left_diag_check(self, r, c, stone):
        n_after, row, col = 0, r + 1, c - 1
        while row < self.m and col >= 0 and self.board[row][col] == stone:
            n_after += 1; row += 1; col -= 1
        n_before, row, col = 0, r - 1, c + 1
        while row >= 0 and col < self.n and self.board[row][col] == stone:
            n_before += 1; row -= 1; col += 1
        return n_after + n_before + 1

    def check_win(self, r, c, stone):
        return any([
            self.row_check(r, c, stone) >= 5,
            self.col_check(r, c, stone) >= 5,
            self.right_diag_check(r, c, stone) >= 5,
            self.left_diag_check(r, c, stone) >= 5
        ])

    def smart_machine_move(self):
        # 1. Block immediate human win (Your 'if max_pos < 5' loop)
        for r in range(self.m):
            for c in range(self.n):
                if self.board[r][c] == ' ':
                    self.board[r][c] = 'O'
                    if self.check_win(r, c, 'O'):
                        self.board[r][c] = 'X'
                        return r, c
                    self.board[r][c] = ' '

        # 2. Proactive Blocking 
        r, c = self.input_row, self.input_col
        max_pos = max(self.row_check(r,c,'O'), self.col_check(r,c,'O'), 
                      self.right_diag_check(r,c,'O'), self.left_diag_check(r,c,'O'))

        # Row blocking
        if max_pos == self.row_check(r, c, 'O'):
            for dc in [1, -1]:
                nc = c + dc
                while 0 <= nc < self.n and self.board[r][nc] == 'O': nc += dc
                if 0 <= nc < self.n and self.board[r][nc] == ' ':
                    self.board[r][nc] = 'X'; return r, nc

        # Column blocking
        if max_pos == self.col_check(r, c, 'O'):
            for dr in [1, -1]:
                nr = r + dr
                while 0 <= nr < self.m and self.board[nr][c] == 'O': nr += dr
                if 0 <= nr < self.m and self.board[nr][c] == ' ':
                    self.board[nr][c] = 'X'; return nr, c

        # Right Diagonal
        if max_pos == self.right_diag_check(r, c, 'O'):
            for d in [1, -1]:
                nr, nc = r + d, c + d
                while 0 <= nr < self.m and 0 <= nc < self.n and self.board[nr][nc] == 'O':
                    nr += d; nc += d
                if 0 <= nr < self.m and 0 <= nc < self.n and self.board[nr][nc] == ' ':
                    self.board[nr][nc] = 'X'; return nr, nc

        # Left Diagonal
        if max_pos == self.left_diag_check(r, c, 'O'):
            for d in [1, -1]:
                nr, nc = r + d, c - d
                while 0 <= nr < self.m and 0 <= nc < self.n and self.board[nr][nc] == 'O':
                    nr += d; nc -= d
                if 0 <= nr < self.m and 0 <= nc < self.n and self.board[nr][nc] == ' ':
                    self.board[nr][nc] = 'X'; return nr, nc


        # 3. Machine logical win
        com_priority = max(self.row_check(r,c,'X'), self.col_check(r,c,'X'), 
                      self.right_diag_check(r,c,'X'), self.left_diag_check(r,c,'X'))

        for r in range(self.m):
            for c in range(self.n):
                if self.board[r][c] == 'X':
                    if com_priority == self.row_check(r, c, 'X'):
                        for dc in [1, -1]:
                            nc = c + dc
                            while 0 <= nc < self.n and self.board[r][nc] == 'X': nc += dc
                            if 0 <= nc < self.n and self.board[r][nc] == ' ':
                                self.board[r][nc] = 'X'; return r, nc
                            
                    if com_priority == self.col_check(r, c, 'X'):
                        for dr in [1, -1]:
                            nr = r + dr
                            while 0 <= nr < self.m and self.board[nr][c] == 'X': nr += dr
                            if 0 <= nr < self.m and self.board[nr][c] == ' ':
                                self.board[nr][c] = 'X'; return nr, c
                            
                    if com_priority == self.right_diag_check(r, c, 'X'):
                        for d in [1, -1]:
                            nr, nc = r + d, c + d
                            while 0 <= nr < self.m and 0 <= nc < self.n and self.board[nr][nc] == 'X':
                                nr += d; nc += d
                            if 0 <= nr < self.m and 0 <= nc < self.n and self.board[nr][nc] == ' ':
                                self.board[nr][nc] = 'X'; return nr, nc
                            
                    if com_priority == self.left_diag_check(r, c, 'X'):
                        for d in [1, -1]:
                            nr, nc = r + d, c - d
                            while 0 <= nr < self.m and 0 <= nc < self.n and self.board[nr][nc] == 'X':
                                nr += d; nc -= d
                            if 0 <= nr < self.m and 0 <= nc < self.n and self.board[nr][nc] == ' ':
                                self.board[nr][nc] = 'X'; return nr, nc
                            
                    
        # 4. Random fallback
        while True:
            rr, rc = random.randint(0, self.m-1), random.randint(0, self.n-1)
            if self.board[rr][rc] == ' ':
                self.board[rr][rc] = 'X'; return rr, rc

game = GomokuGame(15, 15)

@app.route('/')
def index():
    return render_template('index.html', m=game.m, n=game.n)

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    r, c = int(data['row']), int(data['col'])
    option = data.get('option', '2')

    if game.board[r][c] == ' ':
        game.board[r][c] = 'O'
        game.input_row, game.input_col = r, c # Store for AI logic
        
        if game.check_win(r, c, 'O'):
            return jsonify({'status': 'win', 'winner': 'Human', 'r': r, 'c': c})
        
        if option == '1':
            while True:
                mr, mc = random.randint(0, game.m-1), random.randint(0, game.n-1)
                if game.board[mr][mc] == ' ':
                    game.board[mr][mc] = 'X'; break
        else:
            mr, mc = game.smart_machine_move()

        if game.check_win(mr, mc, 'X'):
            return jsonify({'status': 'win', 'winner': 'Machine', 'r': mr, 'c': mc})
            
        return jsonify({'status': 'continue', 'mr': mr, 'mc': mc})
    return jsonify({'status': 'error'})

@app.route('/reset', methods=['POST'])
def reset():
    global game
    game = GomokuGame(15, 15)
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    app.run(debug=True)