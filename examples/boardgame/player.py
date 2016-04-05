import networkzero as nw0

address = nw0.discover("board")

player = input("Which player? ")
#
# Send an empty move to get the state of the board before we begin
#
board = nw0.send_message(address, [player, ""])
#
# Show the current state of the board, request a move, send the move
# the board server and receive the new board state (including any moves
# made by other players).
#
while True:
    print("Board:", board)
    move = input("Move: ")
    board = nw0.send_message(address, [player, move])
