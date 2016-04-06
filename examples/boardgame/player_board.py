"""Show the current state of the board
"""
import networkzero as nw0

def display_board(board):
    print(board)

updates = nw0.discover("board-updates")
while True:
    topic, board = nw0.wait_for_notification(updates, "status")
    print(board) ## or do something more sophisticated
