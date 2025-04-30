import socket
import threading
import time
import logging
from game_room import GameRoom

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class TicTacToeServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.rooms = {}
        self.lock = threading.Lock()

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logging.info(f"Server started on {self.host}:{self.port}")

        while True:
            client_socket, address = self.server_socket.accept()
            logging.info(f"New connection from {address[0]}:{address[1]}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        room_id = None
        player_type = None
        room = None
        buffer = ""

        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    logging.warning("Client disconnected before sending data")
                    client_socket.close()
                    return
                buffer += data
                if '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    try:
                        room_id_str, player_type = line.strip().split('|')
                        room_id = int(room_id_str)
                        break
                    except ValueError:
                        logging.error(f"Invalid initial message: {line}")
                        client_socket.sendall("INVALID_INIT\n".encode())
                        client_socket.close()
                        return

            with self.lock:
                if room_id not in self.rooms:
                    logging.info(f"Creating new room {room_id}")
                    self.rooms[room_id] = GameRoom(room_id)
                room = self.rooms[room_id]

                if not room.add_player(player_type, client_socket):
                    logging.warning(f"Room {room_id} is full for player {player_type}")
                    client_socket.sendall("ROOM_FULL\n".encode())
                    client_socket.close()
                    return

                logging.info(f"Player {player_type} joined room {room_id}")

                if len(room.players) == 2:
                    logging.info(f"Starting game in room {room_id}")
                    self.start_game(room)

            # Initial state request
            client_socket.sendall("GET_STATE\n".encode())

            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    logging.info(f"Player {player_type} in room {room_id} disconnected")
                    break

                with self.lock:
                    if room.game_over:
                        break

                    if data.strip() == "GET_STATE":
                        state = room.get_state()
                        client_socket.sendall(f"BOARD:{''.join(state['board'])}\n".encode())
                        if state['current_player'] == player_type:
                            client_socket.sendall("YOUR_TURN\n".encode())
                        continue

                    # Measure latency start
                    start = time.time()

                    success, response = room.make_move(player_type, data.strip())

                    # Measure latency end
                    end = time.time()
                    latency = end - start
                    logging.info(f"Move latency for player {player_type} in room {room_id}: {latency:.3f}s")

                    if not success:
                        client_socket.sendall(f"{response}\n".encode())
                        if response == "FORFEIT":
                            logging.warning(f"Player {player_type} in room {room_id} forfeited. Player {room.winner} wins!")
                        elif response.startswith("INVALID:"):
                            remaining = response.split(':')[1]
                            logging.warning(f"Player {player_type} in room {room_id} made invalid move. {remaining} attempts left.")
                    else:
                        logging.info(f"Player {player_type} in room {room_id} moved to {data.strip()}.")
                        self.broadcast_game_state(room)

                    if room.game_over:
                        logging.info(f"Game over in room {room_id}. Winner: {room.winner if room.winner else 'Draw'}")
                        self.cleanup_room(room)
                        break

        except (ConnectionResetError, BrokenPipeError):
            logging.warning(f"Player {player_type} disconnected from room {room_id}")
            with self.lock:
                if room_id in self.rooms and room:
                    room.remove_player(player_type)
                    self.cleanup_room(room)
        except Exception as e:
            logging.error(f"Error with player {player_type} in room {room_id}: {str(e)}")
            with self.lock:
                if room_id in self.rooms and room:
                    room.remove_player(player_type)
                    self.cleanup_room(room)
        finally:
            client_socket.close()

    def start_game(self, room):
        room.start_game()
        self.broadcast_game_state(room)

    def broadcast_game_state(self, room):
        state = room.get_state()
        board_state = ''.join(state['board'])
        for player, socket in room.players.items():
            try:
                if room.game_over:
                    if state['winner']:
                        msg = f"WINNER:{state['winner']}|BOARD:{board_state}\n"
                    else:
                        msg = f"DRAW|BOARD:{board_state}\n"
                    socket.sendall(msg.encode())
                else:
                    socket.sendall(f"BOARD:{board_state}\n".encode())
                    if state['current_player'] == player:
                        socket.sendall("YOUR_TURN\n".encode())
            except Exception as e:
                logging.error(f"Error broadcasting to player {player}: {str(e)}")

    def cleanup_room(self, room):
        if room.room_id in self.rooms:
            logging.info(f"Cleaning up room {room.room_id}")
            room.game_over = True
            for player, socket in room.players.items():
                try:
                    socket.close()
                    logging.info(f"Closed connection for player {player}")
                except Exception as e:
                    logging.error(f"Error closing socket: {str(e)}")
            del self.rooms[room.room_id]

if __name__ == "__main__":
    server = TicTacToeServer()
    server.start()
