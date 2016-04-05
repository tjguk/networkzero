import networkzero as nw0

notifications = nw0.advertise("board-updates")
address = nw0.advertise("board")

board = {}
while True:
    command, params = nw0.wait_for_command(address, wait_for_secs=1)
    print("Command %s with params %s" % (command, params))
    
    #
    # Depending on what the command is, update the board or do whatever
    # is needed. 
    #
    if command == "move":
        [player] = params
        board[move] = player
    elif command == "restart":
        board.clear()
    
    #
    # Send a notification to all subscribers that the board has changed
    #
    nw0.send_notification(notifications, "status", board)
