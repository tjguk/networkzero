import networkzero as nw0

def display_board(board):
    print(board)

address = nw0.discover("board")
#
# Send an query to get the state of the board before we begin
#
board = nw0.send_message(address, ["query"])

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
    board = nw0.send_message(address, ["move", player, move])
    display_board(board)
    
    #
    # Only interested in "move" updates, nothing else
    #
    nw0.wait_for_notification(address, "move")
    board = nw0.send_message(address, ["query"])
