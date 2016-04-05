import time
import networkzero as nw0

notifications = nw0.advertise("board-updates")
address = nw0.advertise("board")

board = {}
while True:
    message = nw0.wait_for_message(address)
    segments = message.lower().split()
    command, params = segments[0], segments[1:]
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
    elif command == "query":
        pass
    
    #
    # Return the current state of the board
    #
    nw0.send_reply(address, board)
    #
    # Send a notification to all subscribers that the board has changed
    #
    nw0.send_notification(notifications, command)
