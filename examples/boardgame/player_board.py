import networkzero as nw0

updates = nw0.discover("board-updates")
while True:
    topic, board = nw0.wait_for_notification(updates, "status")
    #
    # Show the latest state of the board
    #
    print()
    print()
    for row in "ABC":
        for column in "123":
            value = board.get("%s%s" % (row, column), "-")
            print(value, sep="", end="")
        print()
