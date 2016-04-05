import networkzero as nw0

address = nw0.discover("reverso")
while True:
    word = input("Enter word: ")
    reversed_word = nw0.send_message(address, word)
    print("Reversed:", reversed_word)
