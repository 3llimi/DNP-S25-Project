import socket
import argparse

host = '127.0.0.1'


parser = argparse.ArgumentParser()
parser.add_argument("port", type=int)
parser.add_argument("number", type=int)
parser.add_argument("type", type=str)
args = parser.parse_args()

port = args.port
room_number = args.number
player_type = args.type


def print_board(board):
    for i in range(0,3):
        for j in range(0,3):
            pos = i * 3 + j
            print(board[pos], end='')
            if j < 2:
                print('|', end='')
            else:
                print('')
        print('-----')


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    print("Connected to server!")

    msg = str(room_number) + '|' + player_type
    s.sendall(msg)

    while True:
        data = s.recv(1024).decode()
        if data == "Move":
            move = input("Move position(0-8): ")
            s.sendall(move)
        elif data.startswith("Board:"):
            print_board(data[6:])
        elif data.startswith("Winner:") or data == "Draw":
            print(data)
        elif data == "INVALID":
            print("Invalid move!")
        else:
            print("Invalid response from server")