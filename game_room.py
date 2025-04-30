class GameRoom:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = {}
        self.board = [' '] * 9
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.invalid_moves = {'X': 0, 'O': 0}
        self.MAX_INVALID_MOVES = 3

    def add_player(self, player_type, socket):
        if player_type in ['X', 'O'] and player_type not in self.players:
            self.players[player_type] = socket
            return True
        return False

    def start_game(self):
        self.board = [' '] * 9
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.invalid_moves = {'X': 0, 'O': 0}

    def make_move(self, player_type, position):
        if self.game_over:
            return False, "GAME_OVER"

        if player_type != self.current_player:
            return False, "NOT_YOUR_TURN"

        try:
            pos = int(position)
            if not 0 <= pos <= 8 or self.board[pos] != ' ':
                raise ValueError
        except ValueError:
            self.invalid_moves[player_type] += 1
            remaining = self.MAX_INVALID_MOVES - self.invalid_moves[player_type]
            
            if remaining <= 0:
                self.handle_forfeit(player_type)
                return False, "FORFEIT"
            
            return False, f"INVALID:{remaining}"

        self.board[pos] = player_type
        self.invalid_moves[player_type] = 0

        if winner := self.check_winner():
            self.game_over = True
            self.winner = winner
            return True, "WINNER"

        if ' ' not in self.board:
            self.game_over = True
            return True, "DRAW"

        self.current_player = 'O' if player_type == 'X' else 'X'
        return True, "MOVED"

    def check_winner(self):
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  
            [0, 4, 8], [2, 4, 6]              
        ]
        for a, b, c in lines:
            if self.board[a] == self.board[b] == self.board[c] != ' ':
                return self.board[a]
        return None

    def handle_forfeit(self, player_type):
        self.game_over = True
        self.winner = 'O' if player_type == 'X' else 'X'
        board_state = ''.join(self.board)
        for p_type, socket in self.players.items():
            try:
                if p_type == player_type:
                    socket.sendall(f"FORFEIT_LOSE|BOARD:{board_state}\n".encode())
                else:
                    socket.sendall(f"FORFEIT_WIN|BOARD:{board_state}\n".encode())
            except:
                pass

    def remove_player(self, player_type):
        if player_type in self.players:
            del self.players[player_type]
            self.game_over = True
            other = 'O' if player_type == 'X' else 'X'
            if other in self.players:
                self.winner = other
                try:
                    self.players[other].sendall("OPPONENT_DISCONNECTED\n".encode())
                except:
                    pass
            else:
                self.winner = None

    def get_state(self):
        return {
            'board': self.board,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner
        }
