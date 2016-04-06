import networkzero as nw0

address = nw0.discover("board")
player = input("Which player? ")

while True:
    move = input("Move: ")
    nw0.send_command(address, "MOVE '%s' '%s'" % (player, move))
