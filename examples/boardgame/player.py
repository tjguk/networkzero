import networkzero as nw0

address = nw0.discover("board")
player = input("Which player? ")
#
# Show the current state of the board, send a move request to the board.
# The board will return the new state of the board which we display.
# Then wait until a move is made by someone else, show the new state
# of the board and go round again.
#
while True:
    move = input("Move: ")
    nw0.send_command(address, "MOVE '%s' '%s'" % (player, move))
