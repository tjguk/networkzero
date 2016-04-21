import networkzero as nw0

address = nw0.discover("reverso")
while True:
    word = input("Enter word: ")
    nw0.send_message_to(address, word)
    reversed_word = nw0.wait_for_message_from(address)
    print("Reversed:", reversed_word)
