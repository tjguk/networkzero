import networkzero as nw0

address = nw0.advertise("board")
board = {}
while True:
    message = nw0.wait_for_message(address)
    #
    # Receive a move from a player
    #
    player, move = message
    
    if move:
        #
        # Do something with the board according to this move, eg:
        #
        board[move] = player
    #
    # Return the current state of the board
    #
    nw0.send_reply(address, board)
