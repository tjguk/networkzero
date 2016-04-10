import networkzero as nw0

address = nw0.discover("board")
player = input("Which player? ")

while True:
    move = input("Move: ")
    nw0.send_message(address, ["MOVE", player, move])
