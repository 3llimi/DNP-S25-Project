import socket
import argparse


def print_board(board):
    if len(board) != 9:
        print(f"\nInvalid board state received: {board}")
        return

    print("\nCurrent Board:")
    for i in range(0, 9, 3):
        print(f" {board[i]} | {board[i+1]} | {board[i+2]} ")
        if i < 6:
            print("-----------")


def handle_player_turn(socket_conn):
    while True:
        try:
            move = input("Your move (0-8): ")
            pos = int(move)
            if 0 <= pos <= 8:
                socket_conn.sendall(move.encode())
                return
            print("Please enter a number 0-8")
        except ValueError:
            print("Invalid input. Please enter a number 0-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("room", type=int)
    parser.add_argument("player", type=str, choices=['X', 'O'])
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        buffer = ""
        try:
            s.connect(('127.0.0.1', args.port))
            s.sendall(f"{args.room}|{args.player}\n".encode())

            s.sendall("GET_STATE\n".encode())

            while True:
                data = s.recv(1024).decode()
                if not data:
                    print("\nConnection closed by server")
                    break
                buffer += data
                while '\n' in buffer:
                    raw_msg, buffer = buffer.split('\n', 1)
                    parts = raw_msg.split('|', 1)

                    if parts[0] == "DRAW":
                        print("\nGame ended in a draw! 🤝")
                        if len(parts) > 1 and parts[1].startswith("BOARD:"):
                            print_board(parts[1][6:])
                        return

                    message = parts[0]
                    if message.startswith("BOARD:"):
                        print_board(message[6:])
                    elif message == "YOUR_TURN":
                        handle_player_turn(s)
                    elif message.startswith("INVALID:"):
                        remaining = message.split(':')[1]
                        print(
                            f"Invalid move! You have {remaining} attempts left")
                        handle_player_turn(s)
                    elif message.startswith("WINNER:"):
                        winner = message.split(':')[1]
                        if len(parts) > 1 and parts[1].startswith("BOARD:"):
                            board = parts[1][6:]
                        else:
                            board = ""
                        if winner == args.player:
                            print("\nYou win! 🎉")
                        else:
                            print("\nYou lose. 😢")
                        print_board(board)
                        return
                    elif message == "FORFEIT_LOSE":
                        print("\nYou forfeited by too many invalid moves!")
                        return
                    elif message == "FORFEIT_WIN":
                        print("\nOpponent forfeited! You win! 🏆")
                        return
                    elif message == "OPPONENT_DISCONNECTED":
                        print("\nOpponent disconnected! You win by default. 🏋")
                        return
                    elif message == "GET_STATE":
                        continue
                    else:
                        print(f"Unknown message: {raw_msg}")
        except Exception as e:
            print(f"Error occurred: {str(e)}")
        finally:
            s.close()


if __name__ == "__main__":
    main()
