import networkzero as nw0

address = nw0.discover("board")

player = input("Which player? ")
board = nw0.send_message(address, [player, None])
while True:
    print("Board:", board)
    move = input("Move: ")
    board = nw0.send_message(address, [player, move])
