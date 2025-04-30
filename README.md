# DNP-S25-Project
This repository hosts the final project for Distributed and Network Programming Course.

A multiplayer Tic-Tac-Toe game using Python sockets, supporting multiple simultaneous games between players.

## Features

- **Multiplayer over network** - Play against friends across different machines
- **Multiple concurrent games** - Server handles many games simultaneously using threading
- **TCP socket communication** - Reliable game state synchronization
- **Turn-based gameplay** - Classic Tic-Tac-Toe rules

## How to run

### Run the server
```bash
$ python3 server.py
```

### Run the client

```console
python3 client.py [port = 5555] [game_room_number] [symbol]
```

Example:
```bash
$ python3 client.py 5555 1 X
```

## Example run and output
```bash
$ python3 server.py 
2025-04-30 23:37:00,947 [INFO] Server started on 127.0.0.1:5555
2025-04-30 23:37:03,507 [INFO] New connection from 127.0.0.1:38206
2025-04-30 23:37:03,507 [INFO] Creating new room 1
2025-04-30 23:37:03,507 [INFO] Player X joined room 1
2025-04-30 23:37:07,831 [INFO] New connection from 127.0.0.1:38210
2025-04-30 23:37:07,832 [INFO] Player O joined room 1
2025-04-30 23:37:07,833 [INFO] Starting game in room 1
2025-04-30 23:37:14,692 [INFO] Move latency for player X in room 1: 0.000s
2025-04-30 23:37:14,693 [INFO] Player X in room 1 moved to 0.
2025-04-30 23:37:21,853 [INFO] Move latency for player O in room 1: 0.000s
2025-04-30 23:37:21,853 [INFO] Player O in room 1 moved to 1.
2025-04-30 23:37:27,838 [INFO] Move latency for player X in room 1: 0.000s
2025-04-30 23:37:27,839 [INFO] Player X in room 1 moved to 4.
2025-04-30 23:37:32,348 [INFO] Move latency for player O in room 1: 0.000s
2025-04-30 23:37:32,348 [INFO] Player O in room 1 moved to 2.
2025-04-30 23:37:36,081 [INFO] Move latency for player X in room 1: 0.000s
2025-04-30 23:37:36,082 [INFO] Player X in room 1 moved to 8.
2025-04-30 23:37:36,084 [INFO] Game over in room 1. Winner: X
2025-04-30 23:37:36,084 [INFO] Cleaning up room 1
2025-04-30 23:37:36,085 [INFO] Closed connection for player X
2025-04-30 23:37:36,085 [INFO] Closed connection for player O
2025-04-30 23:37:36,087 [INFO] Player O in room 1 disconnected
```
```bash
$ python3 client.py 5555 1 X

Current Board:
   |   |   
-----------
   |   |   
-----------
   |   |   
Your move (0-8): 0

Current Board:
 X |   |   
-----------
   |   |   
-----------
   |   |   

Current Board:
 X | O |   
-----------
   |   |   
-----------
   |   |   
Your move (0-8): 4

Current Board:
 X | O |   
-----------
   | X |   
-----------
   |   |   

Current Board:
 X | O | O 
-----------
   | X |   
-----------
   |   |   
Your move (0-8): 8

You win! 🎉

Current Board:
 X | O | O 
-----------
   | X |   
-----------
   |   | X 
```

```bash
$ python3 client.py 5555 1 O

Current Board:
   |   |   
-----------
   |   |   
-----------
   |   |   

Current Board:
 X |   |   
-----------
   |   |   
-----------
   |   |   
Your move (0-8): 1

Current Board:
 X | O |   
-----------
   |   |   
-----------
   |   |   

Current Board:
 X | O |   
-----------
   | X |   
-----------
   |   |   
Your move (0-8): 2

Current Board:
 X | O | O 
-----------
   | X |   
-----------
   |   |   

You lose. 😢

Current Board:
 X | O | O 
-----------
   | X |   
-----------
   |   | X 
```