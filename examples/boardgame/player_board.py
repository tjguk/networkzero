import networkzero as nw0

updates = nw0.discover("board-updates")
while True:
    topic, board = nw0.wait_for_notification(updates, "status")
    print(board) ## or do something more sophisticated
