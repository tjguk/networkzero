import networkzero as nw0

def display_board(board):
    print(board)

address = nw0.discover("board")
updates = nw0.discover("board-updates")
#
# Subscribe to the regular status updates from the board
# server and wait until we receive the first one so we
# what the state of the board is as we enter play.
#
topic, board = nw0.wait_for_notification(updates, "status")

player = input("Which player? ")
#
# Show the current state of the board, send a move request to the board.
# The board will return the new state of the board which we display.
# Then wait until a move is made by someone else, show the new state
# of the board and go round again.
#
while True:
    display_board(board)
    
    move = input("Move: ")
    nw0.send_command(address, "MOVE '%s' '%s'" % (player, move))

    #
    # 
    #
    topic, board = nw0.wait_for_notification(address, "status")
